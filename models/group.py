from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.validator import validate_types

class Group:
    @validate_types
    def __init__(self, group_id: str, name: str, max_capacity: int, creation_date: Optional[str] = None) -> None:
        self.group_id: str = group_id
        self.name: str = name
        self.max_capacity: int = int(max_capacity)
        self.creation_date: str = creation_date if creation_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.student_ids: List[str] = []  # List of student numbers

    @validate_types
    def add_student(self, student_number: str) -> bool:
        if student_number not in self.student_ids:
            self.student_ids.append(student_number)
            return True
        return False

    @validate_types
    def remove_student(self, student_number: str) -> bool:
        if student_number in self.student_ids:
            self.student_ids.remove(student_number)
            return True
        return False

    @validate_types
    def has_vacancy(self) -> bool:
        return self.current_size() < self.max_capacity

    @validate_types
    def current_size(self) -> int:
        return len(self.student_ids)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "name": self.name,
            "max_capacity": self.max_capacity,
            "creation_date": self.creation_date,
            "student_ids": self.student_ids
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Group':
        group = cls(data["group_id"], data["name"], data["max_capacity"], data.get("creation_date"))
        group.student_ids = data.get("student_ids", [])
        return group

    def __str__(self) -> str:
        return f"{self.name} ({self.current_size()}/{self.max_capacity})"
