import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

class SemesterScreen(tk.Frame):
    """
    Displays available semesters.
    - For Users: Simple click-to-navigate interface.
    - For Developers: Selection-based admin tools with an explicit "Continue" button.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        # State variable to track the selected semester for admin tasks.
        self.selected_semester = None
        # Constants for styling to make changes easier.
        self.DEFAULT_BG = "#ffffff"
        self.SELECTED_BG = "#aed6f1" # A light blue to show selection

        # --- Header Frame ---
        header_frame = tk.Frame(self, bg="#f4f6f7")
        header_frame.pack(side="top", fill="x", padx=10, pady=10)
        tk.Button(header_frame, text="← Back to Role Selection", command=self.go_back).pack(side="left")

        # --- Main Content Frame for centering ---
        main_content_frame = tk.Frame(self, bg="#f4f6f7")
        main_content_frame.pack(side="top", fill="both", expand=True)
        
        tk.Label(
            main_content_frame, text="Select a Semester", 
            font=("Helvetica", 32, "bold"), bg="#f4f6f7", fg="#2c3e50"
        ).pack(pady=(20, 10))

        # An instruction label that changes based on the user's role.
        self.instruction_label = tk.Label(
            main_content_frame, font=("Helvetica", 11), bg="#f4f6f7", fg="#34495e"
        )
        self.instruction_label.pack(pady=(0, 20))

        # This frame holds the grid of semester buttons.
        self.button_grid_frame = tk.Frame(main_content_frame, bg="#f4f6f7")
        self.button_grid_frame.pack(pady=20, padx=20)

        # --- Continue Button (for developers only) ---
        self.continue_button = tk.Button(
            main_content_frame, text="Continue to Level Selection", font=("Helvetica", 14, "bold"),
            fg="white", bg="#27ae60", activeforeground="white",
            activebackground="#229954", relief=tk.FLAT, cursor="hand2",
            command=self.on_continue_click
        )
        # It is not packed here; its visibility is managed in on_show_frame.

        # --- Developer Tools Frame ---
        self.dev_tools_frame = tk.Frame(self, bg="#e0e0e0", bd=2, relief=tk.GROOVE)
        self.setup_developer_tools() # Setup is done once during initialization.

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        """Called when the frame is raised. Refreshes UI based on role."""
        # Reset selection state every time the frame is shown.
        self.selected_semester = None
        self.refresh_semester_buttons()
        
        is_dev = self.controller.user_role == "developer"
        if is_dev:
            self.instruction_label.config(text="Select a semester to edit, remove, or continue.")
            self.continue_button.pack(pady=(10, 20))
            self.dev_tools_frame.pack(side="bottom", fill="x", padx=10, pady=10)
            self.update_dev_tool_states() # Ensure buttons are initially disabled.
        else:
            self.instruction_label.config(text="Click a semester to see its levels.")
            self.continue_button.pack_forget() # Hide the continue button for normal users.
            self.dev_tools_frame.pack_forget()

    def refresh_semester_buttons(self):
        """Clears and re-creates semester buttons with role-specific behavior."""
        for widget in self.button_grid_frame.winfo_children():
            widget.destroy()
        
        semesters = self.controller.get_data().keys()
        is_dev = self.controller.user_role == "developer"
        
        for i, semester_name in enumerate(semesters):
            bg_color = self.SELECTED_BG if semester_name == self.selected_semester else self.DEFAULT_BG
            
            button = tk.Button(
                self.button_grid_frame, text=semester_name, font=("Helvetica", 16),
                width=15, pady=20, relief=tk.FLAT, bg=bg_color, bd=1,
            )
            
            # Assign commands based on user role.
            if is_dev:
                # Developer: Single-click only selects the semester.
                button.config(command=lambda s=semester_name: self.on_semester_select(s))
            else:
                # User: Single-click directly navigates.
                button.config(command=lambda s=semester_name: self.navigate_to_semester(s))

            row, col = divmod(i, 3) # Arrange buttons in a grid with 3 columns.
            button.grid(row=row, column=col, padx=15, pady=15)

    def on_semester_select(self, semester_name):
        """Handles single-clicks in developer mode to select/deselect a semester."""
        if self.selected_semester == semester_name:
            self.selected_semester = None # Deselect if clicking the same one again.
        else:
            self.selected_semester = semester_name
        
        logging.info(f"Developer selected semester: '{self.selected_semester}'")
        self.refresh_semester_buttons() # Redraw buttons to show the visual highlight.
        self.update_dev_tool_states() # Update the state of all action buttons.

    def on_continue_click(self):
        """Action for the 'Continue' button, only used by developers."""
        if self.selected_semester:
            self.navigate_to_semester(self.selected_semester)

    def navigate_to_semester(self, semester_name):
        """Sets the current semester in the controller and navigates to the LevelScreen."""
        self.controller.set_current_semester(semester_name)
        self.controller.show_frame("LevelScreen")

    def setup_developer_tools(self):
        """Creates the widgets for the developer panel."""
        tk.Label(self.dev_tools_frame, text="Semester Developer Tools", font=("Helvetica", 14, "bold"), bg="#e0e0e0").pack()
        button_bar = tk.Frame(self.dev_tools_frame, bg="#e0e0e0")
        button_bar.pack(pady=10, fill='x', padx=10)
        
        tk.Button(button_bar, text="Add New Semester", command=self.add_semester).pack(side="left", expand=True, fill='x', padx=5)
        
        self.edit_button = tk.Button(button_bar, text="Edit Selected Name", command=self.edit_semester)
        self.edit_button.pack(side="left", expand=True, fill='x', padx=5)
        
        self.remove_button = tk.Button(button_bar, text="Remove Selected", command=self.remove_semester, bg="#c0392b", fg="white", activebackground="#a93226")
        self.remove_button.pack(side="left", expand=True, fill='x', padx=5)

    def update_dev_tool_states(self):
        """Enables or disables dev buttons based on whether a semester is selected."""
        state = "normal" if self.selected_semester else "disabled"
        self.continue_button.config(state=state)
        self.edit_button.config(state=state)
        self.remove_button.config(state=state)

    def add_semester(self):
        """Opens a dialog to add a new semester."""
        new_semester = simpledialog.askstring("Add Semester", "Enter the name for the new semester:", parent=self)
        if not new_semester or not new_semester.strip(): return

        data = self.controller.get_data()
        if new_semester in data:
            messagebox.showerror("Error", "A semester with this name already exists.", parent=self)
            return
        
        data[new_semester] = {"levels": {}}
        self.controller.save_data(data)
        self.refresh_semester_buttons()
        logging.info(f"Developer added new semester: '{new_semester}'")

    def edit_semester(self):
        """Opens a dialog to rename the currently selected semester."""
        if not self.selected_semester: return

        new_name = simpledialog.askstring(
            "Rename Semester", "Enter the new name for the semester:",
            initialvalue=self.selected_semester, parent=self
        )

        if not new_name or not new_name.strip() or new_name == self.selected_semester:
            return

        data = self.controller.get_data()
        if new_name in data:
            messagebox.showerror("Error", "A semester with this name already exists.", parent=self)
            return

        # To rename a key, copy the data to a new key and delete the old one.
        data[new_name] = data.pop(self.selected_semester)
        self.selected_semester = new_name # Update selection to the new name.
        self.controller.save_data(data)
        self.refresh_semester_buttons()
        logging.info(f"Developer renamed '{self.selected_semester}' to '{new_name}'")

    def remove_semester(self):
        """Asks for confirmation and removes the selected semester."""
        if not self.selected_semester: return

        if messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete the semester '{self.selected_semester}' and all its levels?",
            parent=self
        ):
            data = self.controller.get_data()
            del data[self.selected_semester]
            
            old_selection = self.selected_semester
            self.selected_semester = None # Clear selection.
            
            self.controller.save_data(data)
            self.refresh_semester_buttons()
            self.update_dev_tool_states()
            logging.info(f"Developer removed semester: '{old_selection}'")

    def go_back(self):
        """Navigates back to the RoleSelectionScreen."""
        self.controller.show_frame("RoleSelectionScreen")