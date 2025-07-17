# File: ui/level.py

import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

class LevelScreen(tk.Frame):
    """
    Manages a professionally centered list view of all levels and a detail view.
    This screen displays the levels for the currently selected semester.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        
        self.current_semester = None
        self.current_level_name = None

        # --- Main layout containers ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.list_view = tk.Frame(self, bg="#f0f0f0")
        self.detail_view = tk.Frame(self, bg="#f0f0f0")

        for frame in (self.list_view, self.detail_view):
            frame.grid(row=0, column=0, sticky="nsew")

        self._create_list_view()
        self._create_detail_view()

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event=None):
        """Called when the frame is shown. Sets the current semester and refreshes the list."""
        self.current_semester = self.controller.current_semester
        if not self.current_semester:
            logging.error("LevelScreen shown without a semester being set.")
            self.go_back()
            return
        self.show_list_view()

    def show_list_view(self):
        """Brings the list view to the front and refreshes its content."""
        self.refresh_level_list()
        is_dev = self.controller.user_role == "developer"
        # The button is packed at the bottom; show or hide it based on role.
        if is_dev:
            self._add_level_button.pack(side="bottom", pady=10, padx=20, fill='x', ipady=5)
        else:
            self._add_level_button.pack_forget()
        self.list_view.tkraise()

    def show_detail_view(self, level_name):
        """Shows the detail view for a specific level."""
        self.current_level_name = level_name
        data = self.controller.get_data().get(self.current_semester, {}).get("levels", {}).get(level_name, {})
        
        self._detail_title.config(text=f"Level: {level_name}")
        # Use a Text widget for better formatting of descriptions
        self._detail_description.config(state='normal')
        self._detail_description.delete(1.0, 'end')
        self._detail_description.insert('end', data.get("description", "No description available."))
        self._detail_description.config(state='disabled')

        is_dev = self.controller.user_role == "developer"
        if is_dev:
            self._detail_dev_tools.pack(pady=10, side="bottom")
        else:
            self._detail_dev_tools.pack_forget()
        self.detail_view.tkraise()

    def _create_list_view(self):
        """Builds the widgets for the list view with a centered layout."""
        # 1. Header Frame (Top, non-expanding)
        header_frame = tk.Frame(self.list_view, bg="#f0f0f0")
        header_frame.pack(side="top", fill="x", padx=10, pady=10)
        tk.Button(header_frame, text="← Back to Semesters", command=self.go_back).pack(side="left")

        # 2. Add Level Button (Bottom, non-expanding)
        # We create it here but pack it later in show_list_view.
        self._add_level_button = tk.Button(self.list_view, text="++ Add New Level", command=self.add_level)

        # 3. Main Content Frame (Middle, expanding)
        # This frame fills all available space, centering the content.
        main_content_frame = tk.Frame(self.list_view, bg="#f0f0f0")
        main_content_frame.pack(side="top", fill="both", expand=True)

        # 4. All central content goes inside the main_content_frame
        tk.Label(main_content_frame, text="Levels of Learning", font=("Helvetica", 32, "bold"), bg="#f0f0f0").pack(pady=(20, 10))
        
        tools = tk.Frame(main_content_frame, bg="#f0f0f0")
        tools.pack(pady=5, padx=20, fill='x')
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda n, i, m: self.refresh_level_list())
        tk.Label(tools, text="Search:", bg="#f0f0f0").pack(side="left")
        search_entry = tk.Entry(tools, textvariable=self._search_var)
        search_entry.pack(side="left", fill='x', expand=True, padx=5)
        tk.Button(tools, text="Refresh", command=self.refresh_level_list).pack(side="right")

        # Scrollable area is also inside the main content frame
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

    def _create_detail_view(self):
        """Builds the widgets for the detail view."""
        header = tk.Frame(self.detail_view, bg="#f0f0f0")
        header.pack(pady=10, padx=20, fill='x')
        tk.Button(header, text="← Back to List", command=self.show_list_view).pack(side="left")
        self._detail_title = tk.Label(header, text="", font=("Helvetica", 24, "bold"), bg="#f0f0f0")
        self._detail_title.pack(side="left", expand=True, padx=20)
        
        desc_frame = tk.Frame(self.detail_view, bg="#f0f0f0")
        desc_frame.pack(pady=10, padx=20, fill='both', expand=True)
        tk.Label(desc_frame, text="Level Description:", font=("Helvetica", 12, "bold"), bg="#f0f0f0").pack(anchor='w')
        self._detail_description = tk.Text(desc_frame, font=("Helvetica", 12), wrap="word", bg="white", relief="solid", bd=1, padx=10, pady=10, height=4)
        self._detail_description.pack(fill='both', expand=True)
        self._detail_description.config(state='disabled') # Make it read-only
        
        # Bottom frame for action buttons
        action_frame = tk.Frame(self.detail_view, bg="#f0f0f0")
        action_frame.pack(pady=20, side="bottom")
        tk.Button(action_frame, text="View Concept", font=("Helvetica", 14), command=lambda: self._go_to_content("concept")).pack(side="left", padx=10, ipady=10)
        tk.Button(action_frame, text="View Implementation", font=("Helvetica", 14), command=lambda: self._go_to_content("implementation")).pack(side="left", padx=10, ipady=10)
        
        # Developer tools (hidden by default)
        self._detail_dev_tools = tk.Frame(self.detail_view, bg="#e0e0e0")
        tk.Button(self._detail_dev_tools, text="✏️ Edit This Level", command=lambda: self.edit_level(self.current_level_name)).pack(side="left", padx=10, pady=5)
        tk.Button(self._detail_dev_tools, text="❌ Delete This Level", command=lambda: self.remove_level(self.current_level_name), bg="#c0392b", fg="white").pack(side="left", padx=10, pady=5)

    def _go_to_content(self, path):
        """Navigates to the concept/implementation screen."""
        self.controller.set_current_selection(level=self.current_level_name, path=path)
        self.controller.show_frame("ConceptScreen")

    def refresh_level_list(self):
        """Clears and re-populates the scrollable list of level cards."""
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()
        
        search_term = self._search_var.get().lower()
        if not self.current_semester: return

        levels = self.controller.get_data().get(self.current_semester, {}).get("levels", {})
        for name, data in levels.items():
            if search_term in name.lower():
                self._create_level_card(self._scrollable_frame, name, data)
        self.controller.update_idletasks()

    def _create_level_card(self, parent, name, data):
        """Creates a single card widget for a level in the list view."""
        card = tk.Frame(parent, bd=2, relief="solid", bg="white")
        card.pack(fill='x', padx=10, pady=5)
        
        left_frame = tk.Frame(card, bg="white")
        left_frame.pack(side="left", expand=True, fill='x', padx=10, pady=5)
        tk.Label(left_frame, text=f"{name}", font=("Helvetica", 16, "bold"), bg="white", anchor='w').pack(fill='x')
        tk.Label(left_frame, text=f"{data.get('description', 'No description.')}", bg="white", anchor='w').pack(fill='x', pady=(2,0))
        
        right_frame = tk.Frame(card, bg="white")
        right_frame.pack(side="right", padx=10, pady=10)
        
        tk.Button(right_frame, text="▶ Open", command=lambda n=name: self.show_detail_view(n)).pack(fill='x')
        
        if self.controller.user_role == "developer":
            dev_buttons = tk.Frame(right_frame, bg="white")
            dev_buttons.pack(fill='x', pady=(5,0))
            tk.Button(dev_buttons, text="Edit", command=lambda n=name: self.edit_level(n), width=5).pack(side="left")
            tk.Button(dev_buttons, text="Del", command=lambda n=name: self.remove_level(n), width=5).pack(side="left", padx=5)

    def add_level(self):
        """Opens dialogs to add a new level to the current semester."""
        name = simpledialog.askstring("Add Level", "Enter name for the new level:", parent=self)
        if not name or not name.strip(): return
        
        data = self.controller.get_data()
        if name in data.get(self.current_semester, {}).get("levels", {}):
            messagebox.showerror("Error", "A level with this name already exists in this semester.", parent=self)
            return

        desc = simpledialog.askstring("Add Description", f"Enter description for '{name}':", parent=self)
        if desc is None: return

        # This default structure matches what the main app expects
        data[self.current_semester]["levels"][name] = {
            "description": desc,
            "concept": {"explanation": "New concept explanation...", "code": "", "output": ""},
            "implementation": {"explanation": "New implementation steps...", "code": "", "output": ""}
        }
        self.controller.save_data(data)
        self.refresh_level_list()

    def edit_level(self, level_name):
        """Opens dialogs to edit an existing level's name and description."""
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
            # Rename by moving data to a new key and deleting the old one
            data[self.current_semester]["levels"][new_name] = data[self.current_semester]["levels"].pop(level_name)
        
        data[self.current_semester]["levels"][new_name]['description'] = new_desc
        self.controller.save_data(data)
        self.refresh_level_list()
        
        # If the detail view is showing the level we just edited, update it
        if self.detail_view.winfo_ismapped() and self.current_level_name == level_name:
            self.show_detail_view(new_name)

    def remove_level(self, level_name):
        """Confirms and removes a level from the current semester."""
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to permanently remove '{level_name}'? This cannot be undone."):
            data = self.controller.get_data()
            if level_name in data.get(self.current_semester, {}).get("levels", {}):
                del data[self.current_semester]["levels"][level_name]
                self.controller.save_data(data)
                self.refresh_level_list()
                # If the detail view was showing the deleted level, go back to the list
                if self.detail_view.winfo_ismapped() and self.current_level_name == level_name:
                    self.show_list_view()

    def go_back(self):
        """Navigates back to the semester selection screen."""
        self.controller.show_frame("SemesterScreen")