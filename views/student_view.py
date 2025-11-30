import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.main_controller import MainController
    from models.student import Student

class StudentView(ctk.CTkFrame):
    """
    Interface gráfica para gestão de alunos.
    Herda de ctk.CTkFrame para ser usada numa aba.
    """
    def __init__(self, parent, controller: 'MainController') -> None:
        """
        Inicializa a vista de alunos.

        Args:
            parent: Widget pai.
            controller (MainController): Controlador principal para operações lógicas.
        """
        super().__init__(parent)
        self.controller: 'MainController' = controller
        
        # Configuração da grelha (grid) para responsividade
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) 

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self) -> None:
        """Cria e organiza todos os elementos visuais (botões, entradas, listas)."""
        
        # --- Formulário de Registo ---
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))

        # Configura colunas do formulário para espaçamento igual
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
        form_frame.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(form_frame, text="Registar Aluno", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=7, pady=(10, 15), sticky="w", padx=15)

        # Campo Número
        ctk.CTkLabel(form_frame, text="Número:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_number = ctk.CTkEntry(form_frame, placeholder_text="Ex: 12345")
        self.entry_number.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Campo Nome
        ctk.CTkLabel(form_frame, text="Nome:").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Nome do Aluno")
        self.entry_name.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        # Campo Email
        ctk.CTkLabel(form_frame, text="Email:").grid(row=1, column=4, padx=10, pady=5, sticky="e")
        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="email@my.istec.pt")
        self.entry_email.grid(row=1, column=5, padx=10, pady=5, sticky="ew")

        # Botão de Adicionar
        ctk.CTkButton(form_frame, text="Adicionar", command=self.add_student).grid(row=2, column=0, columnspan=6, padx=10, pady=(5, 15))

        # --- Barra de Pesquisa ---
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(search_frame, text="Pesquisar:").pack(side="left", padx=15, pady=10)
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar por nome, número...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        ctk.CTkButton(search_frame, text="Buscar", command=self.perform_search, width=100).pack(side="left", padx=5, pady=10)
        ctk.CTkButton(search_frame, text="Limpar", command=self.clear_search, fg_color="transparent", border_width=1, width=100).pack(side="left", padx=(5, 15), pady=10)

        # --- Lista de Alunos (Treeview) ---
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Estilo para a tabela
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2b2b2b",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading",
                        background="#1f538d",
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[('active', '#163c66')])

        # Definição das colunas
        columns = ("number", "name", "email", "group", "creationDate")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("number", text="Número")
        self.tree.heading("name", text="Nome")
        self.tree.heading("email", text="Email")
        self.tree.heading("group", text="Grupo")
        self.tree.heading("creationDate", text="Data de Criação")
        
        # Larguras das colunas
        self.tree.column("number", width=100)
        self.tree.column("name", width=200)
        self.tree.column("email", width=200)
        self.tree.column("group", width=100)
        self.tree.column("creationDate", width=100)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        
        # Barra de rolagem
        scrollbar = ctk.CTkScrollbar(list_frame, orientation="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", padx=2, pady=2)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Evento de duplo clique para editar
        self.tree.bind("<Double-1>", self.edit_student)

        # --- Botões de Ação Inferiores ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(side="top", fill="x", padx=10, pady=5)
        ctk.CTkButton(action_frame, text="Editar Aluno", command=self.edit_student).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Transferir", command=self.transfer_student).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Remover Aluno Selecionado", command=self.delete_student, fg_color="#c42b1c", hover_color="#961e14").pack(side="right")

        # Configura o efeito visual de foco nos campos
        self.setup_focus_behavior(self.entry_number)
        self.setup_focus_behavior(self.entry_name)
        self.setup_focus_behavior(self.entry_email)
        self.setup_focus_behavior(self.entry_search)

    def setup_focus_behavior(self, entry):
        """Altera a cor da borda do campo quando ganha/perde foco."""
        default_border = ("#979DA2", "#565B5E")
        focus_border = "#3B8ED0"

        entry.configure(border_color=default_border)
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=focus_border))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=default_border))

    def add_student(self) -> None:
        """Recolhe dados do formulário e chama o controlador para criar o aluno."""
        number = self.entry_number.get().strip()
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()

        try:
            self.controller.create_student(number, name, email)
            messagebox.showinfo("Sucesso", "Aluno registado com sucesso.")
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def edit_student(self, event=None) -> None:
        """Abre a janela de edição se um aluno estiver selecionado."""
        selected = self.tree.selection()
        if not selected:
            if event is None:
                 messagebox.showwarning("Aviso", "Selecione um aluno para editar.")
            return

        item = self.tree.item(selected[0])
        number = item['values'][0]
        
        # Busca o objeto aluno completo para passar à janela de edição
        student = self.controller.get_student(str(number))
        if student:
            EditStudentWindow(self, self.controller, student)

    def delete_student(self) -> None:
        """Remove o aluno selecionado após pedir confirmação."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluno para remover.")
            return

        item = self.tree.item(selected[0])
        number = item['values'][0]

        if messagebox.askyesno("Confirmar", f"Tem a certeza que deseja remover o aluno {number}?"):
            try:
                self.controller.delete_student(str(number))
                messagebox.showinfo("Sucesso", "Aluno removido.")
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

    def transfer_student(self) -> None:
        """Abre a janela de transferência de grupo."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluno para transferir.")
            return

        item = self.tree.item(selected[0])
        number = item['values'][0]
        
        student = self.controller.get_student(str(number))
        if student:
            TransferStudentWindow(self, self.controller, student)

    def clear_form(self) -> None:
        """Limpa os campos de texto do formulário."""
        self.entry_number.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

    def perform_search(self) -> None:
        """Filtra a lista de alunos com base no texto de pesquisa."""
        query = self.entry_search.get().strip()
        if query:
            results = self.controller.search_students(query)
            self.refresh_list(students=results)
        else:
            self.refresh_list()

    def clear_search(self) -> None:
        """Limpa o campo de pesquisa e mostra todos os alunos."""
        self.entry_search.delete(0, tk.END)
        self.refresh_list()

    def refresh_list(self, students: Optional[List['Student']] = None) -> None:
        """
        Atualiza os dados visíveis na tabela (Treeview).
        Se 'students' for None, busca todos do controlador.
        """
        # Limpa tabela atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if students is None:
            students = self.controller.get_all_students()
        
        # Preenche com novos dados
        for s in students:
            group_name = "Sem Grupo"
            if s.group_id:
                group = self.controller.get_group(s.group_id)
                if group:
                    group_name = group.name
            
            self.tree.insert("", "end", values=(s.student_number, s.name, s.email, group_name, s.creation_date))

class EditStudentWindow(ctk.CTkToplevel):
    """Janela modal (pop-up) para editar dados de um aluno."""
    def __init__(self, parent: StudentView, controller: 'MainController', student: 'Student') -> None:
        super().__init__(parent)
        self.controller = controller
        self.student = student
        self.parent_view = parent

        self.title(f"Editar Aluno: {student.name}")
        self.geometry("500x400")
        self.grab_set() # Torna a janela modal (impede interação com a janela principal)

        self.create_widgets()

    def create_widgets(self) -> None:
        """Cria campos de edição."""
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Número é apenas leitura (não se muda a chave primária)
        ctk.CTkLabel(content_frame, text="Número:").pack(pady=(10, 5))
        self.entry_number = ctk.CTkEntry(content_frame)
        self.entry_number.insert(0, self.student.student_number)
        self.entry_number.configure(state="disabled")
        self.entry_number.pack(pady=5)

        ctk.CTkLabel(content_frame, text="Nome:").pack(pady=(10, 5))
        self.entry_name = ctk.CTkEntry(content_frame)
        self.entry_name.insert(0, self.student.name)
        self.entry_name.pack(pady=5)
        self.setup_focus(self.entry_name)

        ctk.CTkLabel(content_frame, text="Email:").pack(pady=(10, 5))
        self.entry_email = ctk.CTkEntry(content_frame)
        self.entry_email.insert(0, self.student.email)
        self.entry_email.pack(pady=5)
        self.setup_focus(self.entry_email)

        ctk.CTkButton(content_frame, text="Guardar", command=self.save).pack(pady=20)

    def setup_focus(self, entry):
        default_border = ("#979DA2", "#565B5E")
        focus_border = "#3B8ED0"
        entry.configure(border_color=default_border)
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=focus_border))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=default_border))

    def save(self) -> None:
        """Chama o controlador para salvar as alterações."""
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()

        try:
            self.controller.update_student(self.student.student_number, name, email)
            messagebox.showinfo("Sucesso", "Aluno atualizado com sucesso.")
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

class TransferStudentWindow(ctk.CTkToplevel):
    """Janela modal para transferir um aluno para outro grupo."""
    def __init__(self, parent: StudentView, controller: 'MainController', student: 'Student') -> None:
        super().__init__(parent)
        self.controller = controller
        self.student = student
        self.parent_view = parent
        
        self.title(f"Transferir Aluno: {student.name}")
        self.geometry("400x250")
        self.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content_frame, text=f"Transferir {self.student.name} para:").pack(pady=10)
        
        # Carrega grupos disponíveis para a combobox
        groups = self.controller.get_all_groups()
        # Filtra para não mostrar o grupo atual do aluno
        self.group_map = {g.name: g.group_id for g in groups if g.group_id != self.student.group_id}
        group_names = list(self.group_map.keys())
        
        if not group_names:
            ctk.CTkLabel(content_frame, text="Não há outros grupos disponíveis.").pack(pady=10)
            return

        self.combo_groups = ctk.CTkComboBox(content_frame, values=group_names)
        self.combo_groups.pack(pady=10)
        
        ctk.CTkButton(content_frame, text="Confirmar Transferência", command=self.confirm).pack(pady=20)
        
    def confirm(self):
        group_name = self.combo_groups.get()
        if not group_name or group_name not in self.group_map:
             messagebox.showerror("Erro", "Selecione um grupo válido.")
             return
             
        group_id = self.group_map[group_name]
        
        try:
            self.controller.transfer_student(self.student.student_number, group_id)
            messagebox.showinfo("Sucesso", "Aluno transferido.")
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
