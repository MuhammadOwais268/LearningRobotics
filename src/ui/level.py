# File: ui/level.py

import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

class LevelScreen(tk.Frame):
    """
    Manages a list view of all levels for a semester.
    This screen acts as a navigator to the Concept and Implementation screens.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        
        self.current_semester = None
        self._create_list_view()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event=None):
        """Called when the frame is shown. Sets the semester and refreshes the list."""
        self.current_semester = self.controller.current_semester
        if not self.current_semester:
            logging.error("LevelScreen shown without a semester being set.")
            self.go_back()
            return
        self.refresh_level_list()
        is_dev = self.controller.user_role == "developer"
        if is_dev:
            self._add_level_button.pack(side="bottom", pady=10, padx=20, fill='x', ipady=5)
        else:
            self._add_level_button.pack_forget()

    def _create_list_view(self):
        """Builds the widgets for the list view with a centered layout."""
        header_frame = tk.Frame(self, bg="#f0f0f0")
        header_frame.pack(side="top", fill="x", padx=10, pady=10)
        tk.Button(header_frame, text="← Back to Semesters", command=self.go_back).pack(side="left")

        self._add_level_button = tk.Button(self, text="++ Add New Level", command=self.add_level)

        main_content_frame = tk.Frame(self, bg="#f0f0f0")
        main_content_frame.pack(side="top", fill="both", expand=True)

        tk.Label(main_content_frame, text="Levels of Learning", font=("Helvetica", 32, "bold"), bg="#f0f0f0").pack(pady=(20, 10))
        
        tools = tk.Frame(main_content_frame, bg="#f0f0f0")
        tools.pack(pady=5, padx=20, fill='x')
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda n, i, m: self.refresh_level_list())
        tk.Label(tools, text="Search:", bg="#f0f0f0").pack(side="left")
        search_entry = tk.Entry(tools, textvariable=self._search_var)
        search_entry.pack(side="left", fill='x', expand=True, padx=5)
        tk.Button(tools, text="Refresh", command=self.refresh_level_list).pack(side="right")

        scroll_container = tk.Frame(main_content_frame)
        scroll_container.pack(fill="both", expand=True, padx=20, pady=10)
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)
        
        canvas = tk.Canvas(scroll_container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self._scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw")
        self._scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def refresh_level_list(self):
        """Clears and re-populates the scrollable list of level cards."""
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()
        
        levels = self.controller.get_data().get(self.current_semester, {}).get("levels", {})
        for name, data in levels.items():
            if self._search_var.get().lower() in name.lower():
                self._create_level_card(self._scrollable_frame, name, data)
        self.controller.update_idletasks()

    def _create_level_card(self, parent, name, data):
        """Creates a card for a level with 'Concept' and 'Implementation' buttons."""
        card = tk.Frame(parent, bd=2, relief="solid", bg="white")
        card.pack(fill='x', padx=10, pady=5)
        
        left_frame = tk.Frame(card, bg="white")
        left_frame.pack(side="left", expand=True, fill='x', padx=10, pady=5)
        tk.Label(left_frame, text=name, font=("Helvetica", 16, "bold"), bg="white", anchor='w').pack(fill='x')
        tk.Label(left_frame, text=data.get('description', 'No description.'), bg="white", anchor='w').pack(fill='x', pady=(2,0))
        
        right_frame = tk.Frame(card, bg="white")
        right_frame.pack(side="right", padx=10, pady=10)
        
        tk.Button(right_frame, text="View Concept", width=18, command=lambda n=name: self.go_to_concept(n)).pack(fill='x', ipady=2)
        tk.Button(right_frame, text="View Implementation", width=18, command=lambda n=name: self.go_to_implementation(n)).pack(fill='x', ipady=2, pady=(5,0))
        
        if self.controller.user_role == "developer":
            tk.Button(right_frame, text="❌ Delete Level", fg="red", command=lambda n=name: self.remove_level(n)).pack(pady=(10,0))

    def go_to_concept(self, level_name):
        self.controller.set_current_selection(level=level_name)
        self.controller.show_frame("ConceptScreen")

    def go_to_implementation(self, level_name):
        self.controller.set_current_selection(level=level_name)
        self.controller.show_frame("ImplementationScreen")

    def add_level(self):
        name = simpledialog.askstring("Add Level", "Enter name for the new level:", parent=self)
        if not name or not name.strip(): return
        
        data = self.controller.get_data()
        if name in data.get(self.current_semester, {}).get("levels", {}):
            messagebox.showerror("Error", "A level with this name already exists.", parent=self)
            return

        desc = simpledialog.askstring("Add Description", f"Enter description for '{name}':", parent=self)
        if desc is None: return

        data[self.current_semester]["levels"][name] = {
            "description": desc,
            "concept": {"explanation": "New concept explanation...", "code": "// New concept code...", "output": "New concept output..."},
            "implementation": {"explanation": "New implementation explanation...", "code": "// New implementation code..."}
        }
        self.controller.save_data(data)
        self.refresh_level_list()

    def remove_level(self, level_name):
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to permanently remove '{level_name}' and all its content?"):
            data = self.controller.get_data()
            if level_name in data.get(self.current_semester, {}).get("levels", {}):
                del data[self.current_semester]["levels"][level_name]
                self.controller.save_data(data)
                self.refresh_level_list()

    def go_back(self):
        self.controller.show_frame("SemesterScreen")