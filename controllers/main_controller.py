import uuid
import re
import unicodedata
from typing import List, Optional
from models.data_manager import DataManager
from models.student import Student
from models.group import Group

class MainController:
    """
    Controlador principal da aplicação.
    Responsável pela lógica de negócio e gestão de alunos e grupos.
    Atua como intermediário entre a Interface (Views) e os Dados (Models).

    Atributos:
        data_manager (DataManager): Instância do gestor de dados.
    """
    def __init__(self) -> None:
        """Inicializa o MainController."""
        self.data_manager: DataManager = DataManager()
        self._observers = []

    def add_observer(self, observer):
        """Adiciona um observador (view) para ser notificado de mudanças."""
        self._observers.append(observer)

    def notify_observers(self):
        """Notifica todos os observadores para atualizarem suas interfaces."""
        for observer in self._observers:
            if hasattr(observer, 'refresh_list'):
                observer.refresh_list()

    def save_data(self) -> None:
        """Guarda os dados persistentemente."""
        self.data_manager.save_data()

    def _normalize(self, text: str) -> str:
        """Normaliza texto para pesquisa (lowercase e sem acentos)."""
        if not text:
            return ""
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()

    # --- Gestão de Alunos ---
    def create_student(self, student_number: str, name: str, email: str) -> Student:
        """
        Cria um novo aluno validando todas as regras de negócio.

        Args:
            student_number (str): Número do aluno.
            name (str): Nome do aluno.
            email (str): Email do aluno.

        Retorna:
            Student: O aluno criado.

        Lança:
            ValueError: Se os dados forem inválidos.
        """
        # Validação: Número de estudante deve conter apenas dígitos
        if not student_number.isdigit():
            raise ValueError("Número de estudante deve conter apenas dígitos.")
        
        # Validação: Número de estudante deve ser único
        if student_number in self.data_manager.students:
            raise ValueError("Número de estudante já registado.")

        # Validação: Campos obrigatórios não podem estar vazios
        if not name or not email or not student_number:
            raise ValueError("Todos os campos são obrigatórios.")
        
        # Validação: O domínio do email deve ser institucional
        if not (email.endswith("@my.istec.pt") or email.endswith("@istec.pt")):
            raise ValueError("O email do aluno deve ser do domínio @my.istec.pt ou @istec.pt")
        
        # Validação: O email deve ser único no sistema
        for s in self.data_manager.students.values():
            if s.email.lower() == email.lower():
                 raise ValueError("Email já registado no sistema.")

        # Validação: O nome deve ter um comprimento mínimo
        if len(name) < 3:
            raise ValueError("O nome deve ter pelo menos 3 caracteres.")
        
        # Validação: O nome não pode conter dígitos numéricos
        if any(char.isdigit() for char in name):
            raise ValueError("O nome não pode conter números.")

        # Criação e armazenamento do aluno
        student = Student(student_number, name, email)
        self.data_manager.students[student_number] = student
        self.save_data()
        self.notify_observers()
        return student

    def update_student(self, student_number: str, name: str, email: str) -> Student:
        """
        Atualiza os dados de um aluno existente.
        """
        if student_number not in self.data_manager.students:
             raise ValueError("Aluno não encontrado.")

        if not name or not email:
            raise ValueError("Todos os campos são obrigatórios.")

        # Validação de domínio de email
        if not (email.endswith("@my.istec.pt") or email.endswith("@istec.pt")):
            raise ValueError("O email do aluno deve ser do domínio @my.istec.pt ou @istec.pt")
        
        # Validação de unicidade de email (excluindo o próprio aluno)
        for s in self.data_manager.students.values():
            if s.email.lower() == email.lower() and s.student_number != student_number:
                 raise ValueError("Email já registado no sistema.")

        # Validação do nome
        if len(name) < 3:
            raise ValueError("O nome deve ter pelo menos 3 caracteres.")
        if any(char.isdigit() for char in name):
            raise ValueError("O nome não pode conter números.")

        # Atualização dos dados
        student = self.data_manager.students[student_number]
        student.name = name
        student.email = email
        self.save_data()
        self.notify_observers()
        return student

    def delete_student(self, student_number: str) -> None:
        """
        Remove um aluno do sistema.
        Se o aluno estiver num grupo, é removido desse grupo também.
        """
        if student_number not in self.data_manager.students:
            raise ValueError("Aluno não encontrado.")
        
        student = self.data_manager.students[student_number]
        
        # Se pertencer a um grupo, remover a referência no grupo
        if student.group_id:
            group = self.data_manager.groups.get(student.group_id)
            if group:
                group.remove_student(student_number)
        
        # Remover do dicionário global de alunos
        del self.data_manager.students[student_number]
        self.save_data()
        self.notify_observers()

    def get_all_students(self) -> List[Student]:
        """Retorna uma lista de todos os alunos."""
        return list(self.data_manager.students.values())

    def search_students(self, query: str) -> List[Student]:
        """Pesquisa alunos por nome, número ou email (case insensitive)."""
        normalized_query = self._normalize(query)
        results = []
        for student in self.data_manager.students.values():
            if (normalized_query in self._normalize(student.name) or 
                normalized_query in str(student.student_number) or 
                normalized_query in self._normalize(student.email)):
                results.append(student)
        return results

    def get_student(self, student_number: str) -> Optional[Student]:
        """Obtém um objeto aluno específico."""
        return self.data_manager.students.get(student_number)

    # --- Gestão de Grupos ---
    def create_group(self, name: str, max_capacity: str, min_capacity: str = "2") -> Group:
        """
        Cria um novo grupo com validações de capacidade e nome.
        """
        # Validação: Nome deve ser alfanumérico
        if not re.match(r'^[a-zA-Z0-9 ]+$', name):
            raise ValueError("O nome do grupo deve conter apenas caracteres alfanuméricos e espaços.")

        # Validação: Nome deve ser único
        for group in self.data_manager.groups.values():
            if group.name.lower() == name.lower():
                raise ValueError("Nome de grupo já existe.")
        
        try:
            # Conversão e validação das capacidades
            max_cap = int(max_capacity)
            if max_cap <= 0:
                raise ValueError("Capacidade máxima deve ser maior que zero.")
            
            min_cap = int(min_capacity)
            if min_cap <= 0:
                raise ValueError("Capacidade mínima deve ser maior que zero.")
            
            # Validação lógica: mín <= máx
            if min_cap > max_cap:
                raise ValueError("Capacidade mínima não pode ser maior que a máxima.")
                
        except ValueError as e:
            if "Capacidade" in str(e):
                raise e
            raise ValueError("Capacidades devem ser números inteiros.")

        # Gera ID único e cria o grupo
        group_id = str(uuid.uuid4())
        group = Group(group_id, name, max_cap, min_cap)
        self.data_manager.groups[group_id] = group
        self.save_data()
        self.notify_observers()
        return group

    def update_group(self, group_id: str, name: str, max_capacity: str, min_capacity: str) -> Group:
        """
        Atualiza dados do grupo, garantindo que a nova capacidade acomoda os membros atuais.
        """
        if group_id not in self.data_manager.groups:
            raise ValueError("Grupo não encontrado.")
            
        group = self.data_manager.groups[group_id]

        if not re.match(r'^[a-zA-Z0-9 ]+$', name):
            raise ValueError("O nome do grupo deve conter apenas caracteres alfanuméricos e espaços.")

        # Verifica unicidade do nome, ignorando o próprio grupo
        for g in self.data_manager.groups.values():
            if g.name.lower() == name.lower() and g.group_id != group_id:
                raise ValueError("Nome de grupo já existe.")
        
        try:
            max_cap = int(max_capacity)
            if max_cap <= 0:
                raise ValueError("Capacidade máxima deve ser maior que zero.")
            
            min_cap = int(min_capacity)
            if min_cap <= 0:
                raise ValueError("Capacidade mínima deve ser maior que zero.")

            if min_cap > max_cap:
                 raise ValueError("Capacidade mínima não pode ser maior que a máxima.")
            
            # Validação Importante: Não pode reduzir capacidade máxima abaixo do número atual de membros
            if max_cap < group.current_size():
                raise ValueError(f"Capacidade máxima não pode ser menor que o número atual de membros ({group.current_size()}).")
                
        except ValueError as e:
            if "Capacidade" in str(e):
                raise e
            raise ValueError("Capacidades devem ser números inteiros.")

        group.name = name
        group.max_capacity = max_cap
        group.min_capacity = min_cap
        self.save_data()
        self.notify_observers()
        return group

    def delete_group(self, group_id: str) -> None:
        """
        Remove um grupo e atualiza os alunos desse grupo para ficarem sem grupo.
        """
        if group_id not in self.data_manager.groups:
            raise ValueError("Grupo não encontrado.")
        
        group = self.data_manager.groups[group_id]
        
        # Remove a referência de grupo de todos os alunos membros
        for s_num in group.student_ids:
            student = self.data_manager.students.get(s_num)
            if student:
                student.group_id = None
        
        del self.data_manager.groups[group_id]
        self.save_data()
        self.notify_observers()

    def get_all_groups(self) -> List[Group]:
        return list(self.data_manager.groups.values())

    def search_groups(self, query: str) -> List[Group]:
        normalized_query = self._normalize(query)
        results = []
        for group in self.data_manager.groups.values():
            if normalized_query in self._normalize(group.name):
                results.append(group)
        return results

    def get_group(self, group_id: str) -> Optional[Group]:
        return self.data_manager.groups.get(group_id)

    # --- Gestão de Associações (Alunos <-> Grupos) ---
    def add_student_to_group(self, student_number: str, group_id: str) -> None:
        """
        Adiciona um aluno a um grupo se houver vaga e o aluno não tiver grupo.
        """
        student = self.data_manager.students.get(student_number)
        group = self.data_manager.groups.get(group_id)

        if not student:
            raise ValueError("Aluno não encontrado.")
        if not group:
            raise ValueError("Grupo não encontrado.")

        # Regra: Um aluno só pode pertencer a um grupo
        if student.group_id:
            raise ValueError(f"Aluno já pertence ao grupo {student.group_id}.")

        # Regra: O grupo não pode exceder a capacidade máxima
        if not group.has_vacancy():
            raise ValueError("Grupo cheio.")

        if group.add_student(student.student_number):
            student.group_id = group.group_id
            self.save_data()
            self.notify_observers()

    def remove_student_from_group(self, student_number: str, group_id: str) -> None:
        """
        Remove um aluno de um grupo, validando a regra de capacidade mínima.
        """
        student = self.data_manager.students.get(student_number)
        group = self.data_manager.groups.get(group_id)

        if not student or not group:
            raise ValueError("Aluno ou Grupo não encontrado.")

        if student.student_number not in group.student_ids:
             raise ValueError("Aluno não pertence a este grupo.")

        # Regra de Integridade: Não remover se o grupo ficar abaixo da capacidade mínima
        # Exceção implícita: Se o grupo está a ser apagado (não é este método)
        if group.current_size() - 1 < group.min_capacity and group.current_size() > 0:
             raise ValueError(f"Não é permitido remover aluno. O grupo ficaria com menos de {group.min_capacity} elementos.")

        if group.remove_student(student_number):
            student.group_id = None
            self.save_data()
            self.notify_observers()

    def get_students_without_group(self) -> List[Student]:
        """Retorna apenas os alunos que ainda não têm grupo."""
        return [s for s in self.data_manager.students.values() if not s.group_id]

    def transfer_student(self, student_number: str, new_group_id: str) -> None:
        """
        Transfere um aluno do grupo atual para um novo grupo.
        Verifica a capacidade do novo grupo e a capacidade mínima do grupo atual.
        """
        student = self.data_manager.students.get(student_number)
        new_group = self.data_manager.groups.get(new_group_id)

        if not student:
            raise ValueError("Aluno não encontrado.")
        if not new_group:
            raise ValueError("Grupo de destino não encontrado.")
        
        if student.group_id == new_group_id:
             raise ValueError("O aluno já pertence a este grupo.")

        if not new_group.has_vacancy():
             raise ValueError("Grupo de destino cheio.")

        # Se o aluno já tem grupo, tenta remover (verificando regra de mínimo)
        if student.group_id:
            current_group = self.data_manager.groups.get(student.group_id)
            if current_group:
                 # Verifica se a saída do aluno viola a regra de mínimo no grupo antigo
                 if current_group.current_size() - 1 < current_group.min_capacity:
                      raise ValueError(f"Não é possível remover do grupo atual ({current_group.name}). Ficaria com menos de {current_group.min_capacity} elementos.")
                 
                 current_group.remove_student(student_number)
        
        # Adiciona ao novo grupo
        new_group.add_student(student_number)
        student.group_id = new_group_id
        self.save_data()
        self.notify_observers()
