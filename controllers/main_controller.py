import uuid
import re
from typing import List, Optional
from utils.validator import validate_types
from models.data_manager import DataManager
from models.student import Student
from models.group import Group

class MainController:
    """
    Controlador principal da aplicação.
    Responsável pela lógica de negócio e gestão de alunos e grupos.

    Attributes:
        data_manager (DataManager): Instância do gestor de dados.
    """
    def __init__(self) -> None:
        """Inicializa o MainController."""
        self.data_manager: DataManager = DataManager()

    def save_data(self) -> None:
        """Persiste os dados através do DataManager."""
        self.data_manager.save_data()

    # --- Student Management ---
    @validate_types
    def create_student(self, student_number: str, name: str, email: str) -> Student:
        """
        Cria um novo aluno.

        Args:
            student_number (str): Número do aluno.
            name (str): Nome do aluno.
            email (str): Email do aluno.

        Returns:
            Student: O aluno criado.

        Raises:
            ValueError: Se os dados forem inválidos ou violarem regras de negócio.
        """
        # RB05: Number digits only
        if not student_number.isdigit():
            raise ValueError("Número de estudante deve conter apenas dígitos.")
        
        # RB06: Unique number
        if student_number in self.data_manager.students:
            raise ValueError("Número de estudante já registado.")

        # Validations (from UC01)
        if not name or not email or not student_number:
            raise ValueError("Todos os campos são obrigatórios.")
        
        # RB07: Email domain validation
        if not (email.endswith("@my.istec.pt") or email.endswith("@istec.pt")):
            raise ValueError("O email do aluno deve ser do domínio @my.istec.pt ou @istec.pt")
        
        # RB08: Email uniqueness
        for s in self.data_manager.students.values():
            if s.email.lower() == email.lower():
                 raise ValueError("Email já registado no sistema.")

        # RB09: Name validation (min length 3, no digits)
        if len(name) < 3:
            raise ValueError("O nome deve ter pelo menos 3 caracteres.")
        if any(char.isdigit() for char in name):
            raise ValueError("O nome não pode conter números.")

        student = Student(student_number, name, email)
        self.data_manager.students[student_number] = student
        self.save_data()
        return student

    @validate_types
    def update_student(self, student_number: str, name: str, email: str) -> Student:
        """
        Atualiza os dados de um aluno existente.

        Args:
            student_number (str): Número do aluno a atualizar.
            name (str): Novo nome.
            email (str): Novo email.

        Returns:
            Student: O aluno atualizado.

        Raises:
            ValueError: Se o aluno não existir ou dados inválidos.
        """
        if student_number not in self.data_manager.students:
             raise ValueError("Aluno não encontrado.")

        # Validations
        if not name or not email:
            raise ValueError("Todos os campos são obrigatórios.")

        # RB07: Email domain validation
        if not (email.endswith("@my.istec.pt") or email.endswith("@istec.pt")):
            raise ValueError("O email do aluno deve ser do domínio @my.istec.pt ou @istec.pt")
        
        # RB08: Email uniqueness (exclude self)
        for s in self.data_manager.students.values():
            if s.email.lower() == email.lower() and s.student_number != student_number:
                 raise ValueError("Email já registado no sistema.")

        # RB09: Name validation (min length 3, no digits)
        if len(name) < 3:
            raise ValueError("O nome deve ter pelo menos 3 caracteres.")
        if any(char.isdigit() for char in name):
            raise ValueError("O nome não pode conter números.")

        student = self.data_manager.students[student_number]
        student.name = name
        student.email = email
        self.save_data()
        return student

    @validate_types
    def delete_student(self, student_number: str) -> None:
        """
        Remove um aluno do sistema.

        Args:
            student_number (str): Número do aluno a remover.

        Raises:
            ValueError: Se o aluno não for encontrado.
        """
        if student_number not in self.data_manager.students:
            raise ValueError("Aluno não encontrado.")
        
        student = self.data_manager.students[student_number]
        
        # RF05: Remove from group automatically
        if student.group_id:
            group = self.data_manager.groups.get(student.group_id)
            if group:
                group.remove_student(student_number)
                # Note: We do not enforce RB04 (min size) here as this is a system-wide deletion
        
        del self.data_manager.students[student_number]
        self.save_data()

    @validate_types
    def get_all_students(self) -> List[Student]:
        """
        Retorna todos os alunos registados.

        Returns:
            List[Student]: Lista de objetos Student.
        """
        return list(self.data_manager.students.values())

    @validate_types
    def search_students(self, query: str) -> List[Student]:
        """
        Pesquisa alunos por nome, número ou email.

        Args:
            query (str): Termo de pesquisa.

        Returns:
            List[Student]: Lista de alunos que correspondem à pesquisa.
        """
        query = query.lower()
        results = []
        for student in self.data_manager.students.values():
            if (query in student.name.lower() or 
                query in str(student.student_number) or 
                query in student.email.lower()):
                results.append(student)
        return results

    @validate_types
    def get_student(self, student_number: str) -> Optional[Student]:
        """
        Obtém um aluno pelo seu número.

        Args:
            student_number (str): Número do aluno.

        Returns:
            Optional[Student]: Objeto Student ou None se não encontrado.
        """
        return self.data_manager.students.get(student_number)

    # --- Group Management ---
    @validate_types
    def create_group(self, name: str, max_capacity: str, min_capacity: str = "2") -> Group:
        """
        Cria um novo grupo de trabalho.

        Args:
            name (str): Nome do grupo.
            max_capacity (str): Capacidade máxima do grupo (como string).
            min_capacity (str, optional): Capacidade mínima. Defaults to "2".

        Returns:
            Group: O grupo criado.

        Raises:
            ValueError: Se dados inválidos ou violação de regras de negócio.
        """
        # RB12: Group name alphanumeric and spaces only
        if not re.match(r'^[a-zA-Z0-9 ]+$', name):
            raise ValueError("O nome do grupo deve conter apenas caracteres alfanuméricos e espaços.")

        # RB03: Unique name
        for group in self.data_manager.groups.values():
            if group.name.lower() == name.lower():
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
                
        except ValueError as e:
            if "Capacidade" in str(e):
                raise e
            raise ValueError("Capacidades devem ser números inteiros.")

        group_id = str(uuid.uuid4())
        group = Group(group_id, name, max_cap, min_cap)
        self.data_manager.groups[group_id] = group
        self.save_data()
        return group

    @validate_types
    def update_group(self, group_id: str, name: str, max_capacity: str, min_capacity: str) -> Group:
        """
        Atualiza os dados de um grupo.

        Args:
            group_id (str): ID do grupo.
            name (str): Novo nome.
            max_capacity (str): Nova capacidade máxima.
            min_capacity (str): Nova capacidade mínima.

        Returns:
            Group: O grupo atualizado.

        Raises:
            ValueError: Se grupo não encontrado ou dados inválidos.
        """
        if group_id not in self.data_manager.groups:
            raise ValueError("Grupo não encontrado.")
            
        group = self.data_manager.groups[group_id]

        # RB12: Group name alphanumeric and spaces only
        if not re.match(r'^[a-zA-Z0-9 ]+$', name):
            raise ValueError("O nome do grupo deve conter apenas caracteres alfanuméricos e espaços.")

        # RB03: Unique name (excluding self)
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
            
            # Validation: New capacity cannot be smaller than current size
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
        return group

    @validate_types
    def delete_group(self, group_id: str) -> None:
        """
        Remove um grupo do sistema e desassocia os alunos.

        Args:
            group_id (str): ID do grupo a remover.

        Raises:
            ValueError: Se o grupo não for encontrado.
        """
        if group_id not in self.data_manager.groups:
            raise ValueError("Grupo não encontrado.")
        
        group = self.data_manager.groups[group_id]
        
        # Update students to remove group reference
        for s_num in group.student_ids:
            student = self.data_manager.students.get(s_num)
            if student:
                student.group_id = None
        
        del self.data_manager.groups[group_id]
        self.save_data()

    @validate_types
    def get_all_groups(self) -> List[Group]:
        """
        Retorna todos os grupos existentes.

        Returns:
            List[Group]: Lista de grupos.
        """
        return list(self.data_manager.groups.values())

    @validate_types
    def search_groups(self, query: str) -> List[Group]:
        """
        Pesquisa grupos por nome.

        Args:
            query (str): Termo de pesquisa.

        Returns:
            List[Group]: Lista de grupos encontrados.
        """
        query = query.lower()
        results = []
        for group in self.data_manager.groups.values():
            if query in group.name.lower():
                results.append(group)
        return results

    @validate_types
    def get_group(self, group_id: str) -> Optional[Group]:
        """
        Obtém um grupo pelo seu ID.

        Args:
            group_id (str): ID do grupo.

        Returns:
            Optional[Group]: Objeto Group ou None se não encontrado.
        """
        return self.data_manager.groups.get(group_id)

    # --- Association Management ---
    @validate_types
    def add_student_to_group(self, student_number: str, group_id: str) -> None:
        """
        Adiciona um aluno a um grupo.

        Args:
            student_number (str): Número do aluno.
            group_id (str): ID do grupo.

        Raises:
            ValueError: Se aluno/grupo não encontrados ou regras violadas (cheio, já tem grupo).
        """
        student = self.data_manager.students.get(student_number)
        group = self.data_manager.groups.get(group_id)

        if not student:
            raise ValueError("Aluno não encontrado.")
        if not group:
            raise ValueError("Grupo não encontrado.")

        # RB01: Exclusivity
        if student.group_id:
            raise ValueError(f"Aluno já pertence ao grupo {student.group_id}.") # Ideally fetch group name

        # RB02: Capacity
        if not group.has_vacancy():
            raise ValueError("Grupo cheio.")

        if group.add_student(student.student_number):
            student.group_id = group.group_id
            self.save_data()
        else:
            # Should not happen given checks, but strictly following bool return
            pass

    @validate_types
    def remove_student_from_group(self, student_number: str, group_id: str) -> None:
        """
        Remove um aluno de um grupo.

        Args:
            student_number (str): Número do aluno.
            group_id (str): ID do grupo.

        Raises:
            ValueError: Se não encontrado, não pertencer, ou violar regra de mínimo.
        """
        student = self.data_manager.students.get(student_number)
        group = self.data_manager.groups.get(group_id)

        if not student or not group:
            raise ValueError("Aluno ou Grupo não encontrado.")

        if student.student_number not in group.student_ids:
             raise ValueError("Aluno não pertence a este grupo.")

        # RB04: Integrity on removal
        # "Não é permitido remover ... se ... resultar num número de elementos inferior ao mínimo"
        # So if current_size <= min_size, we cannot remove (unless we are deleting the group, which is a different op)
        if group.current_size() - 1 < group.min_capacity and group.current_size() > 0:
             # Wait, if I have 2 students (min 2), and I remove 1, I have 1. 1 < 2. So forbidden.
             # What if I have 1 student? (Maybe created in a invalid state or before rule enforcement).
             # Assuming we enforce this strictly.
             raise ValueError(f"Não é permitido remover aluno. O grupo ficaria com menos de {group.min_capacity} elementos.")

        if group.remove_student(student_number):
            student.group_id = None
            self.save_data()
        else:
            # Handle case where student wasn't in list (though checked above)
            pass

    @validate_types
    def get_students_without_group(self) -> List[Student]:
        """
        Retorna lista de alunos que não têm grupo atribuído.

        Returns:
            List[Student]: Alunos sem grupo.
        """
        return [s for s in self.data_manager.students.values() if not s.group_id]

    @validate_types
    def transfer_student(self, student_number: str, new_group_id: str) -> None:
        """
        Transfere um aluno para um novo grupo (RF13).
        
        Args:
            student_number (str): Número do aluno.
            new_group_id (str): ID do grupo de destino.
            
        Raises:
            ValueError: Se validações falharem.
        """
        student = self.data_manager.students.get(student_number)
        new_group = self.data_manager.groups.get(new_group_id)

        if not student:
            raise ValueError("Aluno não encontrado.")
        if not new_group:
            raise ValueError("Grupo de destino não encontrado.")
        
        # Check if already in this group
        if student.group_id == new_group_id:
             raise ValueError("O aluno já pertence a este grupo.")

        # Check destination capacity (RB02)
        if not new_group.has_vacancy():
             raise ValueError("Grupo de destino cheio.")

        # Handle current group removal if exists
        if student.group_id:
            current_group = self.data_manager.groups.get(student.group_id)
            if current_group:
                 # Check RB04 for current group
                 if current_group.current_size() - 1 < current_group.min_capacity:
                      raise ValueError(f"Não é possível remover do grupo atual ({current_group.name}). Ficaria com menos de {current_group.min_capacity} elementos.")
                 
                 # Remove from old
                 current_group.remove_student(student_number)
        
        # Add to new group
        new_group.add_student(student_number)
        student.group_id = new_group_id
        self.save_data()