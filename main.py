import customtkinter as ctk
from controllers.main_controller import MainController
from views.student_view import StudentView
from views.group_view import GroupView

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Grupos de Trabalho")
        self.geometry("900x700")
        
        # Initialize Controller
        self.controller = MainController()

        # UI Setup
        self.create_widgets()
        
        # Save on exit
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Create Tabs
        self.tabview.add("Gerir Alunos")
        self.tabview.add("Gerir Grupos")
        
        # Student View
        self.student_view = StudentView(self.tabview.tab("Gerir Alunos"), self.controller)
        self.student_view.pack(fill="both", expand=True)

        # Group View
        self.group_view = GroupView(self.tabview.tab("Gerir Grupos"), self.controller)
        self.group_view.pack(fill="both", expand=True)

    def on_close(self):
        self.controller.save_data()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()

