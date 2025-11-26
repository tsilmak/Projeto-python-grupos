import tkinter as tk
from tkinter import ttk
from controllers.main_controller import MainController
from views.student_view import StudentView
from views.group_view import GroupView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Grupos de Trabalho")
        self.geometry("800x600")
        
        # Initialize Controller
        self.controller = MainController()

        # UI Setup
        self.create_widgets()
        
        # Save on exit
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.student_view = StudentView(notebook, self.controller)
        self.group_view = GroupView(notebook, self.controller)

        notebook.add(self.student_view, text="Gerir Alunos")
        notebook.add(self.group_view, text="Gerir Grupos")

    def on_close(self):
        self.controller.save_data()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()

