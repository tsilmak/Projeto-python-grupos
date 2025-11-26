import uuid
from models.data_manager import DataManager
from models.student import Student
from models.group import Group

class MainController:
    def __init__(self):
        self.data_manager = DataManager()
        self.min_group_size = 2  # Default per RB02 example

    def save_data(self):
        self.data_manager.save_data()

    # --- Student Management ---
    def create_student(self, student_number, name, email):
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

    def delete_student(self, student_number):
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

    def get_all_students(self):
        return list(self.data_manager.students.values())

    def get_student(self, student_number):
        return self.data_manager.students.get(student_number)

    # --- Group Management ---
    def create_group(self, name, max_capacity):
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

    def delete_group(self, group_id):
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

    def get_all_groups(self):
        return list(self.data_manager.groups.values())

    def get_group(self, group_id):
        return self.data_manager.groups.get(group_id)

    # --- Association Management ---
    def add_student_to_group(self, student_number, group_id):
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
        if group.current_size() >= group.max_capacity:
            raise ValueError("Grupo cheio.")

        group.add_student(student.student_number)
        student.group_id = group.group_id
        self.save_data()

    def remove_student_from_group(self, student_number, group_id):
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

        group.remove_student(student_number)
        student.group_id = None
        self.save_data()

    def get_students_without_group(self):
        return [s for s in self.data_manager.students.values() if not s.group_id]

