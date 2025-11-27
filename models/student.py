from typing import Optional, Dict, Any
from datetime import datetime
from utils.validator import validate_types

class Student:
    """
    Representa um aluno no sistema.

    Attributes:
        student_number (str): O número único do aluno.
        name (str): O nome do aluno.
        email (str): O email do aluno.
        group_id (Optional[str]): O ID do grupo ao qual o aluno pertence.
        creation_date (str): A data de criação do registo do aluno.
    """
    @validate_types
    def __init__(self, student_number: str, name: str, email: str, creation_date: Optional[str] = None) -> None:
        """
        Inicializa uma nova instância de Student.

        Args:
            student_number (str): O número do aluno.
            name (str): O nome do aluno.
            email (str): O email do aluno.
            creation_date (Optional[str], optional): Data de criação. Defaults to None (data atual).
        """
        self.student_number: str = student_number
        self.name: str = name
        self.email: str = email
        self.group_id: Optional[str] = None  # Reference to the group the student belongs to
        self.creation_date: str = creation_date if creation_date else datetime.now().strftime("%d/%m/%Y")

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto Student para um dicionário.

        Returns:
            Dict[str, Any]: Dicionário representando o aluno.
        """
        return {
            "student_number": self.student_number,
            "name": self.name,
            "email": self.email,
            "group_id": self.group_id,
            "creation_date": self.creation_date
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """
        Cria uma instância de Student a partir de um dicionário.

        Args:
            data (Dict[str, Any]): Dados do aluno.

        Returns:
            Student: Instância criada.
        """
        student = cls(data["student_number"], data["name"], data["email"], data.get("creation_date"))
        student.group_id = data.get("group_id")
        return student

    def __str__(self) -> str:
        """
        Retorna a representação em string do aluno.

        Returns:
            str: Nome e número do aluno.
        """
        return f"{self.name} ({self.student_number})"
