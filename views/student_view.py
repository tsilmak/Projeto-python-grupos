import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.main_controller import MainController
    from models.student import Student

class StudentView(ttk.Frame):
    def __init__(self, parent: tk.Widget, controller: 'MainController') -> None:
        super().__init__(parent)
        self.controller: 'MainController' = controller
        
        # UI Layout
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self) -> None:
        # Form Frame
        form_frame = ttk.LabelFrame(self, text="Registar Aluno")
        form_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Número:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_number = ttk.Entry(form_frame)
        self.entry_number.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_name = ttk.Entry(form_frame)
        self.entry_name.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_email = ttk.Entry(form_frame)
        self.entry_email.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(form_frame, text="Adicionar", command=self.add_student).grid(row=0, column=6, padx=10, pady=5)

        # Search Frame
        search_frame = ttk.Frame(self)
        search_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side="left", padx=5)
        self.entry_search = ttk.Entry(search_frame)
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.perform_search).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Limpar", command=self.clear_search).pack(side="left", padx=5)

        # List Frame
        list_frame = ttk.LabelFrame(self, text="Lista de Alunos")
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        columns = ("number", "name", "email", "group")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("number", text="Número")
        self.tree.heading("name", text="Nome")
        self.tree.heading("email", text="Email")
        self.tree.heading("group", text="Grupo")
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Actions
        action_frame = ttk.Frame(self)
        action_frame.pack(side="top", fill="x", padx=10, pady=5)
        ttk.Button(action_frame, text="Remover Aluno Selecionado", command=self.delete_student).pack(side="right")

    def add_student(self) -> None:
        number = self.entry_number.get().strip()
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()

        try:
            self.controller.create_student(number, name, email)
            messagebox.showinfo("Sucesso", "Aluno registado com sucesso.")
            self.clear_form()
            self.refresh_list()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def delete_student(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um aluno para remover.")
            return

        item = self.tree.item(selected[0])
        number = item['values'][0]

        if messagebox.askyesno("Confirmar", f"Tem a certeza que deseja remover o aluno {number}?"):
            try:
                self.controller.delete_student(str(number)) # Ensure it's string as IDs are likely strings
                messagebox.showinfo("Sucesso", "Aluno removido.")
                self.refresh_list()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

    def clear_form(self) -> None:
        self.entry_number.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

    def perform_search(self) -> None:
        query = self.entry_search.get().strip()
        if query:
            results = self.controller.search_students(query)
            self.refresh_list(students=results)
        else:
            self.refresh_list()

    def clear_search(self) -> None:
        self.entry_search.delete(0, tk.END)
        self.refresh_list()

    def refresh_list(self, students: Optional[List['Student']] = None) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if students is None:
            students = self.controller.get_all_students()
        
        for s in students:
            group_name = "Sem Grupo"
            if s.group_id:
                group = self.controller.get_group(s.group_id)
                if group:
                    group_name = group.name
            
            self.tree.insert("", "end", values=(s.student_number, s.name, s.email, group_name))
