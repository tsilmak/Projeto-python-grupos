import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.main_controller import MainController
    from models.group import Group

class GroupView(ctk.CTkFrame):
    def __init__(self, parent, controller: 'MainController') -> None:
        super().__init__(parent)
        self.controller: 'MainController' = controller
        
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self) -> None:
        # Create Group Form
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(form_frame, text="Criar Grupo", font=("Roboto", 16, "bold")).grid(row=0, column=0, columnspan=5, pady=(10, 15), sticky="w", padx=15)

        ctk.CTkLabel(form_frame, text="Nome do Grupo:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Nome do Grupo")
        self.entry_name.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Capacidade Máxima:").grid(row=1, column=2, padx=10, pady=10)
        self.entry_capacity = ctk.CTkEntry(form_frame, width=100, placeholder_text="Ex: 5")
        self.entry_capacity.grid(row=1, column=3, padx=10, pady=10)

        ctk.CTkButton(form_frame, text="Criar", command=self.create_group).grid(row=1, column=4, padx=10, pady=10)

        # Search Frame
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(search_frame, text="Pesquisar:").pack(side="left", padx=15, pady=10)
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Buscar grupo...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        ctk.CTkButton(search_frame, text="Buscar", command=self.perform_search, width=100).pack(side="left", padx=5, pady=10)
        ctk.CTkButton(search_frame, text="Limpar", command=self.clear_search, fg_color="transparent", border_width=1, width=100).pack(side="left", padx=(5, 15), pady=10)

        # List Frame
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        # Ensure Treeview style is consistent
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

        columns = ("name", "capacity", "count", "id")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Nome")
        self.tree.heading("capacity", text="Capacidade")
        self.tree.heading("count", text="Nº Alunos")
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=0, stretch=tk.NO) # Hide ID column
        
        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        
        scrollbar = ctk.CTkScrollbar(list_frame, orientation="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", padx=2, pady=2)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Double click to edit
        self.tree.bind("<Double-1>", self.edit_group)

        # Actions
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(side="top", fill="x", padx=10, pady=5)
        ctk.CTkButton(action_frame, text="Gerir Membros", command=self.manage_group).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Editar Grupo", command=self.edit_group).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Eliminar Grupo", command=self.delete_group, fg_color="#c42b1c", hover_color="#961e14").pack(side="right", padx=5)

        # Setup Focus Behavior
        self.setup_focus_behavior(self.entry_name)
        self.setup_focus_behavior(self.entry_capacity)
        self.setup_focus_behavior(self.entry_search)

    def setup_focus_behavior(self, entry):
        default_border = ("#979DA2", "#565B5E")
        focus_border = "#3B8ED0"

        entry.configure(border_color=default_border)
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=focus_border))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=default_border))

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

    def edit_group(self, event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            if event is None:
                 messagebox.showwarning("Aviso", "Selecione um grupo para editar.")
            return

        item = self.tree.item(selected[0])
        group_id = item['values'][3]
        
        group = self.controller.get_group(group_id)
        if group:
            EditGroupWindow(self, self.controller, group)

    def manage_group(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um grupo para gerir.")
            return

        item = self.tree.item(selected[0])
        group_id = item['values'][3]
        GroupDetailsWindow(self, self.controller, group_id)


class EditGroupWindow(ctk.CTkToplevel):
    def __init__(self, parent: GroupView, controller: 'MainController', group: 'Group') -> None:
        super().__init__(parent)
        self.controller = controller
        self.group = group
        self.parent_view = parent

        self.title(f"Editar Grupo: {group.name}")
        self.geometry("500x400")
        self.grab_set()

        self.create_widgets()

    def create_widgets(self) -> None:
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Name
        ctk.CTkLabel(content_frame, text="Nome do Grupo:").pack(pady=(10, 5))
        self.entry_name = ctk.CTkEntry(content_frame)
        self.entry_name.insert(0, self.group.name)
        self.entry_name.pack(pady=5)
        self.setup_focus(self.entry_name)

        # Capacity
        ctk.CTkLabel(content_frame, text="Capacidade Máxima:").pack(pady=(10, 5))
        self.entry_capacity = ctk.CTkEntry(content_frame)
        self.entry_capacity.insert(0, str(self.group.max_capacity))
        self.entry_capacity.pack(pady=5)
        self.setup_focus(self.entry_capacity)

        # Buttons
        ctk.CTkButton(content_frame, text="Guardar", command=self.save).pack(pady=20)

    def setup_focus(self, entry):
        default_border = ("#979DA2", "#565B5E")
        focus_border = "#3B8ED0"
        entry.configure(border_color=default_border)
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=focus_border))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=default_border))

    def save(self) -> None:
        name = self.entry_name.get().strip()
        capacity = self.entry_capacity.get().strip()

        try:
            self.controller.update_group(self.group.group_id, name, capacity)
            messagebox.showinfo("Sucesso", "Grupo atualizado com sucesso.")
            self.parent_view.refresh_list()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

class GroupDetailsWindow(ctk.CTkToplevel):
    def __init__(self, parent, controller: 'MainController', group_id: str) -> None:
        super().__init__(parent)
        self.controller: 'MainController' = controller
        self.group_id: str = group_id
        self.group: Optional['Group'] = self.controller.get_group(group_id)
        
        if not self.group:
             self.destroy()
             return

        self.title(f"Gerir Grupo: {self.group.name}")
        self.geometry("700x500")
        
        # Make modal
        self.grab_set()
        
        self.create_widgets()
        self.refresh_lists()

    def create_widgets(self) -> None:
        if not self.group: return
        # Info
        info_label = ctk.CTkLabel(self, text=f"Grupo: {self.group.name} | Capacidade: {self.group.max_capacity}", font=("Roboto", 18, "bold"))
        info_label.pack(pady=20)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Available Students
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left_frame, text="Alunos Disponíveis").pack(pady=5)
        
        # List container
        left_list_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        left_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.list_available = tk.Listbox(left_list_frame, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.list_available.pack(side="left", fill="both", expand=True)
        
        scroll_avail = ctk.CTkScrollbar(left_list_frame, orientation="vertical", command=self.list_available.yview)
        scroll_avail.pack(side="right", fill="y")
        self.list_available.configure(yscrollcommand=scroll_avail.set)

        # Buttons
        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Adicionar ->", command=self.add_student).pack(pady=10)
        ctk.CTkButton(btn_frame, text="<- Remover", command=self.remove_student, fg_color="#c42b1c", hover_color="#961e14").pack(pady=10)

        # Group Members
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(right_frame, text="Membros do Grupo").pack(pady=5)
        
        # List container
        right_list_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        right_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.list_members = tk.Listbox(right_list_frame, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.list_members.pack(side="left", fill="both", expand=True)

        scroll_members = ctk.CTkScrollbar(right_list_frame, orientation="vertical", command=self.list_members.yview)
        scroll_members.pack(side="right", fill="y")
        self.list_members.configure(yscrollcommand=scroll_members.set)

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
            if isinstance(self.master.master, GroupView) or isinstance(self.master, GroupView): 
                 # Handle hierarchy: View -> TabView -> App or View -> App
                 # Actually self.master passed in init is GroupView
                 pass
            # However, self.master might be just the CTk instance if we passed that, 
            # but here we passed 'self' from GroupView which is the frame.
            # But Toplevel usually takes root as master internally if not specified or handles it.
            # Let's rely on the passed parent.
            if hasattr(self.master, 'refresh_list'):
                self.master.refresh_list()
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
            if hasattr(self.master, 'refresh_list'):
                self.master.refresh_list()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
