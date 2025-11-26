from typing import Optional, Dict, Any
from utils.validator import validate_types

class Student:
    @validate_types
    def __init__(self, student_number: str, name: str, email: str) -> None:
        self.student_number: str = student_number
        self.name: str = name
        self.email: str = email
        self.group_id: Optional[str] = None  # Reference to the group the student belongs to

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_number": self.student_number,
            "name": self.name,
            "email": self.email,
            "group_id": self.group_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        student = cls(data["student_number"], data["name"], data["email"])
        student.group_id = data.get("group_id")
        return student

    def __str__(self) -> str:
        return f"{self.name} ({self.student_number})"
