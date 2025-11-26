import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.main_controller import MainController
    from models.group import Group

class GroupView(ttk.Frame):
    def __init__(self, parent: tk.Widget, controller: 'MainController') -> None:
        super().__init__(parent)
        self.controller: 'MainController' = controller
        
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self) -> None:
        # Create Group Form
        form_frame = ttk.LabelFrame(self, text="Criar Grupo")
        form_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Nome do Grupo:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = ttk.Entry(form_frame)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Capacidade Máxima:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_capacity = ttk.Entry(form_frame, width=10)
        self.entry_capacity.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(form_frame, text="Criar", command=self.create_group).grid(row=0, column=4, padx=10, pady=5)

        # Search Frame
        search_frame = ttk.Frame(self)
        search_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side="left", padx=5)
        self.entry_search = ttk.Entry(search_frame)
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.perform_search).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Limpar", command=self.clear_search).pack(side="left", padx=5)

        # List Frame
        list_frame = ttk.LabelFrame(self, text="Lista de Grupos")
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        columns = ("name", "capacity", "count", "id")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("name", text="Nome")
        self.tree.heading("capacity", text="Capacidade")
        self.tree.heading("count", text="Nº Alunos")
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=0, stretch=tk.NO) # Hide ID column
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Actions
        action_frame = ttk.Frame(self)
        action_frame.pack(side="top", fill="x", padx=10, pady=5)
        ttk.Button(action_frame, text="Gerir Membros", command=self.manage_group).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Eliminar Grupo", command=self.delete_group).pack(side="right", padx=5)

    def create_group(self) -> None:
        name = self.entry_name.get().strip()
        capacity = self.entry_capacity.get().strip()

        try:
            self.controller.create_group(name, capacity)
            messagebox.showinfo("Sucesso", "Grupo criado com sucesso.")
            self.clear_form()
            self.refresh_list()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def clear_form(self) -> None:
        self.entry_name.delete(0, tk.END)
        self.entry_capacity.delete(0, tk.END)

    def perform_search(self) -> None:
        query = self.entry_search.get().strip()
        if query:
            results = self.controller.search_groups(query)
            self.refresh_list(groups=results)
        else:
            self.refresh_list()

    def clear_search(self) -> None:
        self.entry_search.delete(0, tk.END)
        self.refresh_list()

    def refresh_list(self, groups: Optional[List['Group']] = None) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if groups is None:
            groups = self.controller.get_all_groups()
            
        for g in groups:
            self.tree.insert("", "end", values=(g.name, g.max_capacity, g.current_size(), g.group_id))

    def delete_group(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um grupo.")
            return

        item = self.tree.item(selected[0])
        group_id = item['values'][3]
        
        if messagebox.askyesno("Confirmar", "Tem a certeza que deseja eliminar este grupo?"):
            try:
                self.controller.delete_group(group_id)
                self.refresh_list()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

    def manage_group(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um grupo para gerir.")
            return

        item = self.tree.item(selected[0])
        group_id = item['values'][3]
        GroupDetailsWindow(self, self.controller, group_id)


class GroupDetailsWindow(tk.Toplevel):
    def __init__(self, parent: tk.Widget, controller: 'MainController', group_id: str) -> None:
        super().__init__(parent)
        self.controller: 'MainController' = controller
        self.group_id: str = group_id
        self.group: Optional['Group'] = self.controller.get_group(group_id)
        
        if not self.group:
             self.destroy()
             return

        self.title(f"Gerir Grupo: {self.group.name}")
        self.geometry("600x400")

        self.create_widgets()
        self.refresh_lists()

    def create_widgets(self) -> None:
        if not self.group: return
        # Info
        info_label = ttk.Label(self, text=f"Grupo: {self.group.name} | Capacidade: {self.group.max_capacity}")
        info_label.pack(pady=10)

        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=10)

        # Available Students
        left_frame = ttk.LabelFrame(content_frame, text="Alunos Disponíveis (Sem Grupo)")
        left_frame.pack(side="left", fill="both", expand=True)
        
        self.list_available = tk.Listbox(left_frame)
        self.list_available.pack(fill="both", expand=True, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Adicionar ->", command=self.add_student).pack(pady=5)
        ttk.Button(btn_frame, text="<- Remover", command=self.remove_student).pack(pady=5)

        # Group Members
        right_frame = ttk.LabelFrame(content_frame, text="Membros do Grupo")
        right_frame.pack(side="right", fill="both", expand=True)
        
        self.list_members = tk.Listbox(right_frame)
        self.list_members.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_lists(self) -> None:
        self.list_available.delete(0, tk.END)
        self.list_members.delete(0, tk.END)

        # Available
        available = self.controller.get_students_without_group()
        for s in available:
            self.list_available.insert(tk.END, f"{s.student_number} - {s.name}")

        # Members
        # Reload group to get fresh data
        self.group = self.controller.get_group(self.group_id)
        if self.group:
            for s_num in self.group.student_ids:
                student = self.controller.get_student(s_num)
                if student:
                    self.list_members.insert(tk.END, f"{student.student_number} - {student.name}")

    def add_student(self) -> None:
        selection = self.list_available.curselection()
        if not selection:
            return
        
        text = self.list_available.get(selection[0])
        student_number = text.split(" - ")[0]

        try:
            self.controller.add_student_to_group(student_number, self.group_id)
            self.refresh_lists()
            if isinstance(self.master, GroupView): # Type check safe
                self.master.refresh_list() # Update parent list counts
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def remove_student(self) -> None:
        selection = self.list_members.curselection()
        if not selection:
            return
        
        text = self.list_members.get(selection[0])
        student_number = text.split(" - ")[0]

        try:
            self.controller.remove_student_from_group(student_number, self.group_id)
            self.refresh_lists()
            if isinstance(self.master, GroupView):
                self.master.refresh_list() # Update parent list counts
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
