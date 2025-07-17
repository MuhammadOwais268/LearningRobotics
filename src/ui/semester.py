import tkinter as tk
from tkinter import messagebox
import logging
import json
import os

class SemesterScreen(tk.Frame):
    """
    Displays available semesters. Provides administrative tools (Add, Edit, Remove)
    for developers, with data persisted in a JSON file.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.data_file = os.path.join(project_root, 'data', 'semesters.json')

        self.semesters = self.load_data()
        self._selected_semester = None

        # --- Header Frame (for Title and Back Button) ---
        header_frame = tk.Frame(self, bg="#f4f6f7")
        header_frame.pack(pady=20, padx=20, fill="x")

        # --- ADDED: Back Button ---
        back_button = tk.Button(
            header_frame, text="← Back to Role Selection", font=("Helvetica", 10),
            fg="#34495e", bg="#f4f6f7", relief=tk.FLAT,
            cursor="hand2", command=self.go_back
        )
        back_button.pack(side="left", anchor="n")
        
        tk.Label(
            header_frame, text="Select a Semester", font=("Helvetica", 24, "bold"),
            bg="#f4f6f7", fg="#2c3e50"
        ).pack(side="left", expand=True)

        self.semester_display_frame = tk.Frame(self, bg="#f4f6f7")
        self.semester_display_frame.pack(pady=(0, 20), padx=20, fill="both", expand=True)

        self.button_grid_frame = tk.Frame(self.semester_display_frame, bg="#f4f6f7")
        self.button_grid_frame.pack()

        self.dev_tools_frame = tk.Frame(self, bg="#e0e0e0", bd=2, relief=tk.GROOVE)

        self.setup_developer_tools()
        self.refresh_semester_buttons()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        """Shows/hides dev tools based on role."""
        if self.controller.user_role == "developer":
            self.dev_tools_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        else:
            self.dev_tools_frame.pack_forget()

    def load_data(self):
        """Loads semester list from the JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            default_data = ["Semester 1", "Semester 2", "Semester 3"]
            self.save_data(default_data)
            return default_data

    def save_data(self, data):
        """Saves the semester list to the JSON file."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Semester data saved to '{self.data_file}'")

    def refresh_semester_buttons(self):
        """Clears and re-creates the grid of semester buttons."""
        for widget in self.button_grid_frame.winfo_children():
            widget.destroy()
        for i, semester_name in enumerate(self.semesters):
            button = tk.Button(
                self.button_grid_frame, text=semester_name, font=("Helvetica", 14),
                width=15, pady=15, command=lambda s=semester_name: self.select_semester(s)
            )
            row, col = divmod(i, 4)
            button.grid(row=row, column=col, padx=10, pady=10)
        self._reset_selection()

    def select_semester(self, semester_name):
        """Handles a click on a semester button."""
        if self.controller.user_role == 'developer':
            self._selected_semester = semester_name
            self._selected_label.config(text=f"Selected: {semester_name}")
            self._edit_entry.delete(0, 'end')
            self._edit_entry.insert(0, semester_name)
        else:
            messagebox.showinfo("Action", f"Proceeding to '{semester_name}'...", parent=self)

    def setup_developer_tools(self):
        """Creates the widgets for the developer panel."""
        tk.Label(self.dev_tools_frame, text="Developer Tools", font=("Helvetica", 14, "bold"), bg="#e0e0e0").pack(pady=5)
        add_frame = tk.Frame(self.dev_tools_frame, bg="#e0e0e0")
        add_frame.pack(pady=5, padx=10, fill='x')
        self._new_semester_entry = tk.Entry(add_frame, font=("Helvetica", 12))
        self._new_semester_entry.pack(side="left", ipady=4, expand=True, fill='x')
        tk.Button(add_frame, text="Add Semester", command=self.add_semester).pack(side="left", padx=10)
        edit_frame = tk.Frame(self.dev_tools_frame, bg="#e0e0e0")
        edit_frame.pack(pady=5, padx=10, fill='x')
        self._selected_label = tk.Label(edit_frame, text="Selected: None", font=("Helvetica", 10, "italic"), bg="#e0e0e0")
        self._selected_label.pack(anchor='w')
        self._edit_entry = tk.Entry(edit_frame, font=("Helvetica", 12))
        self._edit_entry.pack(pady=(5, 10), ipady=4, expand=True, fill='x')
        button_bar = tk.Frame(edit_frame, bg="#e0e0e0")
        button_bar.pack(fill='x')
        tk.Button(button_bar, text="Update Name", command=self.edit_semester).pack(side="left", expand=True, fill='x')
        tk.Button(button_bar, text="Remove Selected", command=self.remove_semester, bg="#c0392b", fg="white").pack(side="left", padx=10, expand=True, fill='x')

    def add_semester(self):
        """Adds a new semester."""
        new_name = self._new_semester_entry.get().strip()
        if not new_name or new_name in self.semesters: return
        self.semesters.append(new_name)
        self.save_data(self.semesters)
        self.refresh_semester_buttons()
        self._new_semester_entry.delete(0, 'end')

    def edit_semester(self):
        """Updates the name of the currently selected semester."""
        if not self._selected_semester: return
        new_name = self._edit_entry.get().strip()
        if not new_name or (new_name in self.semesters and new_name != self._selected_semester): return
        try:
            index = self.semesters.index(self._selected_semester)
            self.semesters[index] = new_name
            self.save_data(self.semesters)
            self.refresh_semester_buttons()
        except ValueError: pass
        self._reset_selection()
        
    def remove_semester(self):
        """Removes the currently selected semester."""
        if not self._selected_semester: return
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{self._selected_semester}'?"):
            self.semesters.remove(self._selected_semester)
            self.save_data(self.semesters)
            self.refresh_semester_buttons()

    def _reset_selection(self):
        """Clears the selection state in the developer tools UI."""
        self._selected_semester = None
        if hasattr(self, '_selected_label'):
            self._selected_label.config(text="Selected: None")
            self._edit_entry.delete(0, 'end')

    def go_back(self):
        """Navigates back to the RoleSelectionScreen."""
        logging.info("Navigating back from Semester to Role Selection screen.")
        self.controller.show_frame("RoleSelectionScreen")