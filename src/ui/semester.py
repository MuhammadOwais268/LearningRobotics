import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

class SemesterScreen(tk.Frame):
    """
    Displays available semesters in a clean, centered layout.
    Provides administrative tools for developers.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller

        # --- Header Frame (Stays at the top) ---
        header_frame = tk.Frame(self, bg="#f4f6f7")
        header_frame.pack(side="top", fill="x", padx=10, pady=10)
        tk.Button(header_frame, text="← Back to Role Selection", command=self.go_back).pack(side="left")

        # --- THIS IS THE KEY: A Main Content Frame that will be centered ---
        main_content_frame = tk.Frame(self, bg="#f4f6f7")
        # By packing with expand=True, this frame will take up the central space
        main_content_frame.pack(side="top", fill="both", expand=True)
        
        # --- Widgets are now placed inside this centered frame ---
        tk.Label(
            main_content_frame, text="Select a Semester", 
            font=("Helvetica", 32, "bold"), bg="#f4f6f7", fg="#2c3e50"
        ).pack(pady=(20, 30))

        # This frame holds the grid of buttons, and it's also inside the main content frame
        self.button_grid_frame = tk.Frame(main_content_frame, bg="#f4f6f7")
        self.button_grid_frame.pack(pady=20, padx=20)

        # --- Developer Tools Frame (Stays at the bottom) ---
        self.dev_tools_frame = tk.Frame(self, bg="#e0e0e0", bd=2, relief=tk.GROOVE)
        
        # We still define the dev tools, but they are packed later
        self.setup_developer_tools()

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        """Called when the frame is raised. Refreshes buttons and dev tools."""
        self.refresh_semester_buttons()
        if self.controller.user_role == "developer":
            # Pack the dev tools at the bottom when needed
            self.dev_tools_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        else:
            self.dev_tools_frame.pack_forget()

    def refresh_semester_buttons(self):
        """Clears and re-creates semester buttons from the central data source."""
        for widget in self.button_grid_frame.winfo_children():
            widget.destroy()
        
        semesters = self.controller.get_data().keys()
        for i, semester_name in enumerate(semesters):
            button = tk.Button(
                self.button_grid_frame, text=semester_name, font=("Helvetica", 16),
                width=15, pady=20, relief=tk.FLAT, bg="#ffffff", bd=1,
                command=lambda s=semester_name: self.select_semester(s)
            )
            # Use grid for neat alignment of buttons
            row, col = divmod(i, 3) # 3 buttons per row
            button.grid(row=row, column=col, padx=15, pady=15)

    def select_semester(self, semester_name):
        """Sets the current semester in the controller and navigates to the LevelScreen."""
        self.controller.set_current_semester(semester_name)
        self.controller.show_frame("LevelScreen")

    def setup_developer_tools(self):
        """Creates the widgets for the developer panel."""
        tk.Label(self.dev_tools_frame, text="Semester Developer Tools", font=("Helvetica", 14, "bold"), bg="#e0e0e0").pack()
        button_bar = tk.Frame(self.dev_tools_frame, bg="#e0e0e0")
        button_bar.pack(pady=10, fill='x', padx=10)
        tk.Button(button_bar, text="Add New Semester", command=self.add_semester).pack(side="left", expand=True, fill='x', padx=5)
        # For now, Edit and Remove are disabled as they are more complex at the semester level
        tk.Button(button_bar, text="Edit Selected (WIP)", state="disabled").pack(side="left", expand=True, fill='x', padx=5)
        tk.Button(button_bar, text="Remove Selected (WIP)", state="disabled", bg="#c0392b", fg="white").pack(side="left", expand=True, fill='x', padx=5)

    def add_semester(self):
        """Opens a dialog to add a new semester."""
        new_semester = simpledialog.askstring("Add Semester", "Enter the name for the new semester:", parent=self)
        if not new_semester or not new_semester.strip():
            return

        data = self.controller.get_data()
        if new_semester in data:
            messagebox.showerror("Error", "A semester with this name already exists.", parent=self)
            return
        
        data[new_semester] = {"levels": {}} # Add new semester with an empty levels dict
        self.controller.save_data(data)
        self.refresh_semester_buttons()
        logging.info(f"Developer added new semester: '{new_semester}'")

    def go_back(self):
        """Navigates back to the RoleSelectionScreen."""
        self.controller.show_frame("RoleSelectionScreen")