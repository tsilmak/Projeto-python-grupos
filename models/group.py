from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.validator import validate_types

class Group:
    """
    Representa um grupo de trabalho.

    Attributes:
        group_id (str): O identificador único do grupo.
        name (str): O nome do grupo.
        max_capacity (int): A capacidade máxima do grupo.
        min_capacity (int): A capacidade mínima do grupo.
        creation_date (str): A data de criação do grupo.
        student_ids (List[str]): Lista de IDs dos alunos no grupo.
    """
    @validate_types
    def __init__(self, group_id: str, name: str, max_capacity: int, min_capacity: int = 2, creation_date: Optional[str] = None) -> None:
        """
        Inicializa uma nova instância de Group.

        Args:
            group_id (str): ID do grupo.
            name (str): Nome do grupo.
            max_capacity (int): Capacidade máxima.
            min_capacity (int, optional): Capacidade mínima. Defaults to 2.
            creation_date (Optional[str], optional): Data de criação. Defaults to None.
        """
        self.group_id: str = group_id
        self.name: str = name
        self.max_capacity: int = int(max_capacity)
        self.min_capacity: int = int(min_capacity)
        self.creation_date: str = creation_date if creation_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.student_ids: List[str] = []  # List of student numbers

    @validate_types
    def add_student(self, student_number: str) -> bool:
        """
        Adiciona um aluno ao grupo.

        Args:
            student_number (str): Número do aluno a adicionar.

        Returns:
            bool: True se adicionado com sucesso, False se já existir.
        """
        if student_number not in self.student_ids:
            self.student_ids.append(student_number)
            return True
        return False

    @validate_types
    def remove_student(self, student_number: str) -> bool:
        """
        Remove um aluno do grupo.

        Args:
            student_number (str): Número do aluno a remover.

        Returns:
            bool: True se removido com sucesso, False se não existir.
        """
        if student_number in self.student_ids:
            self.student_ids.remove(student_number)
            return True
        return False

    @validate_types
    def has_vacancy(self) -> bool:
        """
        Verifica se o grupo tem vagas disponíveis.

        Returns:
            bool: True se houver vagas, False caso contrário.
        """
        return self.current_size() < self.max_capacity

    @validate_types
    def current_size(self) -> int:
        """
        Retorna o número atual de alunos no grupo.

        Returns:
            int: Número de alunos.
        """
        return len(self.student_ids)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto Group para um dicionário.

        Returns:
            Dict[str, Any]: Dicionário representando o grupo.
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
        Cria uma instância de Group a partir de um dicionário.

        Args:
            data (Dict[str, Any]): Dados do grupo.

        Returns:
            Group: Instância criada.
        """
        group = cls(data["group_id"], data["name"], data["max_capacity"], data.get("min_capacity", 2), data.get("creation_date"))
        group.student_ids = data.get("student_ids", [])
        return group

    def __str__(self) -> str:
        """
        Retorna a representação em string do grupo.

        Returns:
            str: Nome e capacidade do grupo.
        """
        return f"{self.name} ({self.current_size()}/{self.max_capacity})"
