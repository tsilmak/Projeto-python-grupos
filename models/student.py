class Student:
    def __init__(self, student_number, name, email):
        self.student_number = student_number
        self.name = name
        self.email = email
        self.group_id = None  # Reference to the group the student belongs to

    def to_dict(self):
        return {
            "student_number": self.student_number,
            "name": self.name,
            "email": self.email,
            "group_id": self.group_id
        }

    @classmethod
    def from_dict(cls, data):
        student = cls(data["student_number"], data["name"], data["email"])
        student.group_id = data.get("group_id")
        return student

    def __str__(self):
        return f"{self.name} ({self.student_number})"

