import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.main_controller import MainController
    from models.student import Student

class StudentView(ctk.CTkFrame):
    def __init__(self, parent, controller: 'MainController') -> None:
        super().__init__(parent)
        self.controller: 'MainController' = controller
        
        # Configure grid expansion
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # List frame expands

        # UI Layout
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self) -> None:
        # Form Frame
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(form_frame, text="Registar Aluno", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=7, pady=(10, 15), sticky="w", padx=15)

        ctk.CTkLabel(form_frame, text="Número:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_number = ctk.CTkEntry(form_frame, placeholder_text="Ex: 12345")
        self.entry_number.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Nome:").grid(row=1, column=2, padx=10, pady=10)
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Nome do Aluno")
        self.entry_name.grid(row=1, column=3, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Email:").grid(row=1, column=4, padx=10, pady=10)
        self.entry_email = ctk.CTkEntry(form_frame, placeholder_text="email@exemplo.com")
        self.entry_email.grid(row=1, column=5, padx=10, pady=10)

        ctk.CTkButton(form_frame, text="Adicionar", command=self.add_student).grid(row=1, column=6, padx=10, pady=10)

        # Search Frame
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(search_frame, text="Pesquisar:").pack(side="left", padx=15, pady=10)
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar por nome, número...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        ctk.CTkButton(search_frame, text="Buscar", command=self.perform_search, width=100).pack(side="left", padx=5, pady=10)
        ctk.CTkButton(search_frame, text="Limpar", command=self.clear_search, fg_color="transparent", border_width=1, width=100).pack(side="left", padx=(5, 15), pady=10)

        # List Frame
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Treeview Style
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

        columns = ("number", "name", "email", "group")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("number", text="Número")
        self.tree.heading("name", text="Nome")
        self.tree.heading("email", text="Email")
        self.tree.heading("group", text="Grupo")
        
        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        
        scrollbar = ctk.CTkScrollbar(list_frame, orientation="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", padx=2, pady=2)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Double click to edit
        self.tree.bind("<Double-1>", self.edit_student)

        # Actions
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(side="top", fill="x", padx=10, pady=5)
        ctk.CTkButton(action_frame, text="Editar Aluno", command=self.edit_student).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Remover Aluno Selecionado", command=self.delete_student, fg_color="#c42b1c", hover_color="#961e14").pack(side="right")

        # Setup Focus Behavior
        self.setup_focus_behavior(self.entry_number)
        self.setup_focus_behavior(self.entry_name)
        self.setup_focus_behavior(self.entry_email)
        self.setup_focus_behavior(self.entry_search)

    def setup_focus_behavior(self, entry):
        default_border = ("#979DA2", "#565B5E")
        focus_border = "#3B8ED0"

        entry.configure(border_color=default_border)
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=focus_border))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=default_border))

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

    def edit_student(self, event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            if event is None: # Only show warning if clicked button
                 messagebox.showwarning("Aviso", "Selecione um aluno para editar.")
            return

        item = self.tree.item(selected[0])
        number = item['values'][0]
        
        student = self.controller.get_student(str(number))
        if student:
            EditStudentWindow(self, self.controller, student)

    def delete_student(self) -> None:
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

class EditStudentWindow(ctk.CTkToplevel):
    def __init__(self, parent: StudentView, controller: 'MainController', student: 'Student') -> None:
        super().__init__(parent)
        self.controller = controller
        self.student = student
        self.parent_view = parent

        self.title(f"Editar Aluno: {student.name}")
        self.geometry("500x400")
        self.grab_set() # Modal

        self.create_widgets()

    def create_widgets(self) -> None:
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Number (Read-only)
        ctk.CTkLabel(content_frame, text="Número:").pack(pady=(10, 5))
        self.entry_number = ctk.CTkEntry(content_frame)
        self.entry_number.insert(0, self.student.student_number)
        self.entry_number.configure(state="disabled") # Cannot change ID
        self.entry_number.pack(pady=5)

        # Name
        ctk.CTkLabel(content_frame, text="Nome:").pack(pady=(10, 5))
        self.entry_name = ctk.CTkEntry(content_frame)
        self.entry_name.insert(0, self.student.name)
        self.entry_name.pack(pady=5)
        self.setup_focus(self.entry_name)

        # Email
        ctk.CTkLabel(content_frame, text="Email:").pack(pady=(10, 5))
        self.entry_email = ctk.CTkEntry(content_frame)
        self.entry_email.insert(0, self.student.email)
        self.entry_email.pack(pady=5)
        self.setup_focus(self.entry_email)

        # Buttons
        ctk.CTkButton(content_frame, text="Guardar", command=self.save).pack(pady=20)

    def setup_focus(self, entry):
        # Reusing focus logic roughly or could import/mixin
        default_border = ("#979DA2", "#565B5E")
        focus_border = "#3B8ED0"
        entry.configure(border_color=default_border)
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=focus_border))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=default_border))

    def save(self) -> None:
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()

        try:
            self.controller.update_student(self.student.student_number, name, email)
            messagebox.showinfo("Sucesso", "Aluno atualizado com sucesso.")
            self.parent_view.refresh_list()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
