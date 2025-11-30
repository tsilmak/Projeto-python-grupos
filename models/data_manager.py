import json
import os
import sys
from typing import Dict, Any
from models.student import Student
from models.group import Group

# Determina o caminho correto para o ficheiro de dados
# Se estiver a executar como executável compilado, usa a pasta do executável
# Caso contrário, usa a pasta onde o script está localizado
if getattr(sys, 'frozen', False):
    # Se está executando como executável compilado (PyInstaller)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Se está executando como script Python
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FILE = os.path.join(BASE_DIR, "data.json")

class DataManager:
    """
    Gestor de persistência de dados.
    Carrega e guarda dados num ficheiro JSON.

    Atributos:
        students (Dict[str, Student]): Dicionário de alunos (chave: número de estudante).
        groups (Dict[str, Group]): Dicionário de grupos (chave: ID do grupo).
    """
    def __init__(self) -> None:
        """Inicializa o DataManager e carrega os dados automaticamente."""
        self.students: Dict[str, Student] = {}
        self.groups: Dict[str, Group] = {}
        self.load_data()

    def load_data(self) -> None:
        """
        Carrega os dados do ficheiro JSON para a memória.
        Se o ficheiro não existir, não faz nada (inicia vazio).
        """
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Carrega a lista de alunos e converte para objetos Student
                for s_data in data.get("students", []):
                    student = Student.from_dict(s_data)
                    self.students[student.student_number] = student
                
                # Carrega a lista de grupos e converte para objetos Group
                for g_data in data.get("groups", []):
                    group = Group.from_dict(g_data)
                    self.groups[group.group_id] = group

        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao carregar dados: {e}")

    def save_data(self) -> None:
        """
        Guarda os dados atuais (alunos e grupos) no ficheiro JSON.
        Sobrescreve o ficheiro existente.
        """
        # Converte todos os objetos em memória para dicionários
        data = {
            "students": [s.to_dict() for s in self.students.values()],
            "groups": [g.to_dict() for g in self.groups.values()]
        }
        try:
            # Escreve no ficheiro com indentação para legibilidade
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erro ao guardar dados: {e}")
