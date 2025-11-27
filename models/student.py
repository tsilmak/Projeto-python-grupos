from typing import Optional, Dict, Any
from datetime import datetime

class Student:
    """
    Representa um aluno no sistema.

    Atributos:
        student_number (str): O número único do aluno.
        name (str): O nome do aluno.
        email (str): O email do aluno.
        group_id (Optional[str]): O ID do grupo ao qual o aluno pertence.
        creation_date (str): A data de criação do registo do aluno.
    """
    def __init__(self, student_number: str, name: str, email: str, creation_date: Optional[str] = None) -> None:
        """
        Inicializa um novo Aluno.

        Args:
            student_number (str): O número do aluno.
            name (str): O nome do aluno.
            email (str): O email do aluno.
            creation_date (Optional[str], optional): Data de criação. Predefinição: None (data atual).
        """
        self.student_number: str = student_number
        self.name: str = name
        self.email: str = email
        self.group_id: Optional[str] = None  # Referência ao grupo a que o aluno pertence
        
        # Se nenhuma data for fornecida, usa a data atual formatada como dd/mm/aaaa
        self.creation_date: str = creation_date if creation_date else datetime.now().strftime("%d/%m/%Y")

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto Aluno num dicionário.
        Utilizado para facilitar a gravação em ficheiro JSON.

        Retorna:
            Dict[str, Any]: Dicionário com os dados do aluno.
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
        Cria uma instância de Aluno a partir de um dicionário.
        Utilizado ao carregar dados do ficheiro JSON.

        Args:
            data (Dict[str, Any]): Dados do aluno.

        Retorna:
            Student: Instância criada.
        """
        student = cls(data["student_number"], data["name"], data["email"], data.get("creation_date"))
        student.group_id = data.get("group_id")
        return student

    def __str__(self) -> str:
        """
        Representação em texto do aluno.
        
        Retorna:
            str: Nome e número do aluno formatados.
        """
        return f"{self.name} ({self.student_number})"
