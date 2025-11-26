import json
import os
from models.student import Student
from models.group import Group

DATA_FILE = "data.json"

class DataManager:
    def __init__(self):
        self.students = {}  # Map student_number -> Student object
        self.groups = {}    # Map group_id -> Group object
        self.load_data()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Load students
                for s_data in data.get("students", []):
                    student = Student.from_dict(s_data)
                    self.students[student.student_number] = student
                
                # Load groups
                for g_data in data.get("groups", []):
                    group = Group.from_dict(g_data)
                    self.groups[group.group_id] = group

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data: {e}")

    def save_data(self):
        data = {
            "students": [s.to_dict() for s in self.students.values()],
            "groups": [g.to_dict() for g in self.groups.values()]
        }
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving data: {e}")

