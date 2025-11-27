from typing import List, Dict, Any, Optional
from datetime import datetime

class Group:
    """
    Representa um grupo de trabalho.

    Atributos:
        group_id (str): Identificador único do grupo.
        name (str): Nome do grupo.
        max_capacity (int): Capacidade máxima.
        min_capacity (int): Capacidade mínima.
        creation_date (str): Data de criação.
        student_ids (List[str]): Lista de IDs dos alunos no grupo.
    """
    def __init__(self, group_id: str, name: str, max_capacity: int, min_capacity: int = 2, creation_date: Optional[str] = None) -> None:
        """
        Inicializa um novo Grupo.

        Args:
            group_id (str): ID do grupo.
            name (str): Nome do grupo.
            max_capacity (int): Capacidade máxima.
            min_capacity (int, optional): Capacidade mínima. Predefinição: 2.
            creation_date (Optional[str], optional): Data de criação.
        """
        self.group_id: str = group_id
        self.name: str = name
        self.max_capacity: int = int(max_capacity)
        self.min_capacity: int = int(min_capacity)
        # Define a data de criação atual se não for fornecida
        self.creation_date: str = creation_date if creation_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.student_ids: List[str] = []  # Lista que armazena apenas os números dos alunos (IDs)

    def add_student(self, student_number: str) -> bool:
        """
        Adiciona um aluno ao grupo.
        Verifica apenas se o aluno já está na lista, não verifica capacidade aqui (feito no controlador).

        Args:
            student_number (str): Número do aluno.

        Retorna:
            bool: True se adicionado, False se já existir.
        """
        if student_number not in self.student_ids:
            self.student_ids.append(student_number)
            return True
        return False

    def remove_student(self, student_number: str) -> bool:
        """
        Remove um aluno do grupo.

        Args:
            student_number (str): Número do aluno.

        Retorna:
            bool: True se removido, False se não existir.
        """
        if student_number in self.student_ids:
            self.student_ids.remove(student_number)
            return True
        return False

    def has_vacancy(self) -> bool:
        """
        Verifica se há vagas no grupo.
        Compara o número atual de alunos com a capacidade máxima.

        Retorna:
            bool: True se houver vagas, False caso contrário.
        """
        return self.current_size() < self.max_capacity

    def current_size(self) -> int:
        """
        Número atual de alunos no grupo.

        Retorna:
            int: Número de alunos.
        """
        return len(self.student_ids)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o grupo para dicionário.
        Utilizado para serialização em JSON.

        Retorna:
            Dict[str, Any]: Dados do grupo.
        """
        return {
            "group_id": self.group_id,
            "name": self.name,
            "max_capacity": self.max_capacity,
            "min_capacity": self.min_capacity,
            "creation_date": self.creation_date,
            "student_ids": self.student_ids
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Group':
        """
        Cria um Grupo a partir de um dicionário.
        Utilizado para carregar dados do JSON.

        Args:
            data (Dict[str, Any]): Dados do grupo.

        Retorna:
            Group: Instância criada.
        """
        group = cls(data["group_id"], data["name"], data["max_capacity"], data.get("min_capacity", 2), data.get("creation_date"))
        group.student_ids = data.get("student_ids", [])
        return group

    def __str__(self) -> str:
        """
        Representação em texto do grupo.

        Retorna:
            str: Nome e capacidade (atual/máxima).
        """
        return f"{self.name} ({self.current_size()}/{self.max_capacity})"
