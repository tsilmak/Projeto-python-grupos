import customtkinter as ctk
from controllers.main_controller import MainController
from views.student_view import StudentView
from views.group_view import GroupView

# Configuração global da aparência do CustomTkinter
ctk.set_appearance_mode("System")  # Usa o tema do sistema (Dark/Light)
ctk.set_default_color_theme("blue") 

class App(ctk.CTk):
    """
    Classe principal da aplicação.
    Configura a janela e inicializa os componentes.
    """
    def __init__(self):
        super().__init__()
        self.title("Gestor de Grupos de Trabalho")
        self.geometry("900x700")
        
        # Inicializa o controlador central
        self.controller = MainController()

        # Cria a interface
        self.create_widgets()
        
        # Garante que os dados são salvos ao fechar a janela
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """Cria o sistema de abas e adiciona as vistas."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Adiciona abas
        self.tabview.add("Gerir Alunos")
        self.tabview.add("Gerir Grupos")
        
        # Inicializa a vista de alunos na primeira aba
        self.student_view = StudentView(self.tabview.tab("Gerir Alunos"), self.controller)
        self.student_view.pack(fill="both", expand=True)

        # Inicializa a vista de grupos na segunda aba
        self.group_view = GroupView(self.tabview.tab("Gerir Grupos"), self.controller)
        self.group_view.pack(fill="both", expand=True)

    def on_close(self):
        """Executado quando a janela é fechada."""
        self.controller.save_data()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
