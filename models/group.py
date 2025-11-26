from datetime import datetime

class Group:
    def __init__(self, group_id, name, max_capacity, creation_date=None):
        self.group_id = group_id
        self.name = name
        self.max_capacity = int(max_capacity)
        self.creation_date = creation_date if creation_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.student_ids = []  # List of student numbers

    def add_student(self, student_number):
        if student_number not in self.student_ids:
            self.student_ids.append(student_number)

    def remove_student(self, student_number):
        if student_number in self.student_ids:
            self.student_ids.remove(student_number)

    def current_size(self):
        return len(self.student_ids)

    def to_dict(self):
        return {
            "group_id": self.group_id,
            "name": self.name,
            "max_capacity": self.max_capacity,
            "creation_date": self.creation_date,
            "student_ids": self.student_ids
        }

    @classmethod
    def from_dict(cls, data):
        group = cls(data["group_id"], data["name"], data["max_capacity"], data.get("creation_date"))
        group.student_ids = data.get("student_ids", [])
        return group

    def __str__(self):
        return f"{self.name} ({self.current_size()}/{self.max_capacity})"

