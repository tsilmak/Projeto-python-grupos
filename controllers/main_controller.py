import uuid
from typing import List, Optional
from utils.validator import validate_types
from models.data_manager import DataManager
from models.student import Student
from models.group import Group

class MainController:
    def __init__(self) -> None:
        self.data_manager: DataManager = DataManager()
        self.min_group_size: int = 2  # Default per RB02 example

    def save_data(self) -> None:
        self.data_manager.save_data()

    # --- Student Management ---
    @validate_types
    def create_student(self, student_number: str, name: str, email: str) -> Student:
        # RB05: Number digits only
        if not student_number.isdigit():
            raise ValueError("Número de estudante deve conter apenas dígitos.")
        
        # RB06: Unique number
        if student_number in self.data_manager.students:
            raise ValueError("Número de estudante já registado.")

        # Validations (from UC01)
        if not name or not email or not student_number:
            raise ValueError("Todos os campos são obrigatórios.")
        
        if "@" not in email: # Simple validation
            raise ValueError("Email inválido.")

        student = Student(student_number, name, email)
        self.data_manager.students[student_number] = student
        self.save_data()
        return student

    @validate_types
    def delete_student(self, student_number: str) -> None:
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
        return list(self.data_manager.students.values())

    @validate_types
    def search_students(self, query: str) -> List[Student]:
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
        return self.data_manager.students.get(student_number)

    # --- Group Management ---
    @validate_types
    def create_group(self, name: str, max_capacity: str) -> Group:
        # RB03: Unique name
        for group in self.data_manager.groups.values():
            if group.name.lower() == name.lower():
                raise ValueError("Nome de grupo já existe.")
        
        try:
            max_cap = int(max_capacity)
            if max_cap <= 0:
                raise ValueError("Capacidade deve ser maior que zero.")
        except ValueError:
            raise ValueError("Capacidade deve ser um número inteiro.")

        group_id = str(uuid.uuid4())
        group = Group(group_id, name, max_cap)
        self.data_manager.groups[group_id] = group
        self.save_data()
        return group

    @validate_types
    def delete_group(self, group_id: str) -> None:
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
        return list(self.data_manager.groups.values())

    @validate_types
    def search_groups(self, query: str) -> List[Group]:
        query = query.lower()
        results = []
        for group in self.data_manager.groups.values():
            if query in group.name.lower():
                results.append(group)
        return results

    @validate_types
    def get_group(self, group_id: str) -> Optional[Group]:
        return self.data_manager.groups.get(group_id)

    # --- Association Management ---
    @validate_types
    def add_student_to_group(self, student_number: str, group_id: str) -> None:
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
        student = self.data_manager.students.get(student_number)
        group = self.data_manager.groups.get(group_id)

        if not student or not group:
            raise ValueError("Aluno ou Grupo não encontrado.")

        if student.student_number not in group.student_ids:
             raise ValueError("Aluno não pertence a este grupo.")

        # RB04: Integrity on removal
        # "Não é permitido remover ... se ... resultar num número de elementos inferior ao mínimo"
        # So if current_size <= min_size, we cannot remove (unless we are deleting the group, which is a different op)
        if group.current_size() - 1 < self.min_group_size and group.current_size() > 0:
             # Wait, if I have 2 students (min 2), and I remove 1, I have 1. 1 < 2. So forbidden.
             # What if I have 1 student? (Maybe created in a invalid state or before rule enforcement).
             # Assuming we enforce this strictly.
             raise ValueError(f"Não é permitido remover aluno. O grupo ficaria com menos de {self.min_group_size} elementos.")

        if group.remove_student(student_number):
            student.group_id = None
            self.save_data()
        else:
            # Handle case where student wasn't in list (though checked above)
            pass

    @validate_types
    def get_students_without_group(self) -> List[Student]:
        return [s for s in self.data_manager.students.values() if not s.group_id]
