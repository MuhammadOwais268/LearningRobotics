import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

class LevelScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        
        self.current_semester = None
        self.current_level_name = None

        self.list_view = tk.Frame(self, bg="#f4f6f7")
        self.detail_view = tk.Frame(self, bg="#f4f6f7")

        for frame in (self.list_view, self.detail_view):
            frame.grid(row=0, column=0, sticky="nsew")

        self._create_list_view()
        self._create_detail_view()

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        self.current_semester = self.controller.current_semester
        if not self.current_semester:
            logging.error("LevelScreen shown without a semester being set.")
            self.go_back()
            return
        self.show_list_view()

    def show_list_view(self):
        self.refresh_level_list()
        self.list_view.tkraise()
        is_dev = self.controller.user_role == "developer"
        if is_dev:
            self._add_level_button.pack(side="bottom", pady=10, padx=20, fill='x', ipady=5)
        else:
            self._add_level_button.pack_forget()

    def show_detail_view(self, level_name):
        self.current_level_name = level_name
        data = self.controller.get_data().get(self.current_semester, {}).get("levels", {}).get(level_name, {})
        self._detail_title.config(text=f"🔍 Level: {level_name}")
        self._detail_description.config(text=data.get("description", "No description."))
        is_dev = self.controller.user_role == "developer"
        if is_dev:
            self._detail_dev_tools.pack(pady=10, side="bottom")
        else:
            self._detail_dev_tools.pack_forget()
        self.detail_view.tkraise()

    def _create_list_view(self):
        header = tk.Frame(self.list_view, bg="#f4f6f7")
        header.pack(pady=10, padx=20, fill='x')
        
        tk.Button(header, text="← Back to Semesters", command=self.go_back).pack(side="left", anchor='n')
        tk.Label(header, text="📚 Levels of Learning", font=("Helvetica", 24, "bold"), bg="#f4f6f7", fg="#2c3e50").pack(side="left", expand=True)
        
        tools = tk.Frame(self.list_view, bg="#f4f6f7")
        tools.pack(pady=5, padx=20, fill='x')
        
        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda n, i, m: self.refresh_level_list())
        
        tk.Label(tools, text="🔍 Search:", bg="#f4f6f7").pack(side="left")
        
        search_entry = tk.Entry(tools, textvariable=self._search_var)
        tk.Button(tools, text="🔃 Refresh", command=self.refresh_level_list).pack(side="right", padx=(5, 0))
        search_entry.pack(side="left", fill='x', expand=True)

        self._add_level_button = tk.Button(self.list_view, text="+➕ Add New Level", command=self.add_level)

        scroll_container = tk.Frame(self.list_view)
        scroll_container.pack(fill="both", expand=True, padx=20, pady=(5,0))
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(scroll_container, bg="#f4f6f7", highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        canvas.configure(yscrollcommand=scrollbar.set)
        
        self._scrollable_frame = tk.Frame(canvas, bg="#f4f6f7")
        canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw")
        self._scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _create_detail_view(self):
        header = tk.Frame(self.detail_view, bg="#f4f6f7")
        header.pack(pady=10, padx=20, fill='x')
        tk.Button(header, text="← Back to List", command=self.show_list_view).pack(side="left")
        self._detail_title = tk.Label(header, text="", font=("Helvetica", 24, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self._detail_title.pack(side="left", expand=True)

        desc_frame = tk.Frame(self.detail_view, bg="#f4f6f7")
        desc_frame.pack(pady=10, padx=20, fill='both', expand=True)
        tk.Label(desc_frame, text="📋 Level Description:", font=("Helvetica", 12, "bold"), bg="#f4f6f7").pack(anchor='w')
        self._detail_description = tk.Label(desc_frame, text="", font=("Helvetica", 12), wraplength=550, justify="left", bg="#ffffff", anchor='nw', bd=1, relief='solid', padx=10, pady=10)
        self._detail_description.pack(fill='both', expand=True)
        
        path_button_frame = tk.Frame(self.detail_view, bg="#f4f6f7")
        path_button_frame.pack(pady=20, side="bottom")
        tk.Button(path_button_frame, text="View Concept", font=("Helvetica", 14), command=lambda: self._go_to_content("concept")).pack(side="left", padx=10, ipady=10)
        tk.Button(path_button_frame, text="View Implementation", font=("Helvetica", 14), command=lambda: self._go_to_content("implementation")).pack(side="left", padx=10, ipady=10)

        self._detail_dev_tools = tk.Frame(self.detail_view, bg="#e0e0e0")
        tk.Button(self._detail_dev_tools, text="✏️ Edit This Level", command=lambda: self.edit_level(self.current_level_name)).pack(side="left", padx=10, pady=5)
        tk.Button(self._detail_dev_tools, text="❌ Delete This Level", command=lambda: self.remove_level(self.current_level_name), bg="#c0392b", fg="white").pack(side="left", padx=10, pady=5)

    def _go_to_content(self, path):
        self.controller.set_current_selection(level=self.current_level_name, path=path)
        self.controller.show_frame("ConceptScreen")

    def refresh_level_list(self):
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()
        search_term = self._search_var.get().lower()
        levels = self.controller.get_data().get(self.current_semester, {}).get("levels", {})
        for name, data in levels.items():
            if search_term in name.lower():
                self._create_level_card(self._scrollable_frame, name, data)
        self.controller.update_idletasks()

    def _create_level_card(self, parent, name, data):
        card = tk.Frame(parent, bd=2, relief="solid", bg="white")
        card.pack(fill='x', padx=10, pady=5)
        left_frame = tk.Frame(card, bg="white")
        left_frame.pack(side="left", expand=True, fill='x', padx=10, pady=10)
        tk.Label(left_frame, text=f"▣ {name}", font=("Helvetica", 16, "bold"), bg="white", anchor='w').pack(fill='x')
        tk.Label(left_frame, text=f"📝 {data.get('description', 'No description.')}", bg="white", anchor='w').pack(fill='x')
        right_frame = tk.Frame(card, bg="white")
        right_frame.pack(side="right", padx=10, pady=10)
        tk.Button(right_frame, text="▶ Open", command=lambda n=name: self.show_detail_view(n)).pack(fill='x')
        if self.controller.user_role == "developer":
            dev_buttons = tk.Frame(right_frame, bg="white")
            dev_buttons.pack(fill='x', pady=5)
            tk.Button(dev_buttons, text="✏️ Edit", command=lambda n=name: self.edit_level(n)).pack(side="left")
            tk.Button(dev_buttons, text="❌ Delete", command=lambda n=name: self.remove_level(n)).pack(side="left", padx=5)

    def add_level(self):
        name = simpledialog.askstring("Add Level", "Enter name for the new level:", parent=self)
        if not name or not name.strip(): return
        desc = simpledialog.askstring("Add Description", f"Enter description for '{name}':", parent=self)
        if desc is None: return
        data = self.controller.get_data()
        if name in data.get(self.current_semester, {}).get("levels", {}):
            messagebox.showerror("Error", "A level with this name already exists.", parent=self)
            return
        data[self.current_semester]["levels"][name] = {"description": desc, "concept": "# New Concept\n\nEnter theory here.", "implementation": "// New Implementation\n\nEnter code here."}
        self.controller.save_data(data)
        self.refresh_level_list()

    def edit_level(self, level_name):
        data = self.controller.get_data()
        current_data = data.get(self.current_semester, {}).get("levels", {}).get(level_name, {})
        new_name = simpledialog.askstring("Edit Name", "Enter new level name:", initialvalue=level_name, parent=self)
        if not new_name or not new_name.strip(): return
        new_desc = simpledialog.askstring("Edit Description", "Enter new description:", initialvalue=current_data.get("description", ""), parent=self)
        if new_desc is None: return
        if new_name != level_name:
            if new_name in data[self.current_semester]["levels"]:
                messagebox.showerror("Error", "Another level with this name already exists.", parent=self)
                return
            data[self.current_semester]["levels"][new_name] = data[self.current_semester]["levels"].pop(level_name)
        data[self.current_semester]["levels"][new_name]['description'] = new_desc
        self.controller.save_data(data)
        self.refresh_level_list()
        if self.detail_view.winfo_ismapped():
            self.show_detail_view(new_name)

    def remove_level(self, level_name):
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to permanently remove '{level_name}'?"):
            data = self.controller.get_data()
            if level_name in data.get(self.current_semester, {}).get("levels", {}):
                del data[self.current_semester]["levels"][level_name]
                self.controller.save_data(data)
                self.refresh_level_list()
                if self.detail_view.winfo_ismapped() and self.current_level_name == level_name:
                    self.show_list_view()

    def go_back(self):
        self.controller.show_frame("SemesterScreen")