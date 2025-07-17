import tkinter as tk
from tkinter import messagebox
import logging
import json
import os

class SemesterScreen(tk.Frame):
    """
    Displays available semesters. Provides administrative tools for developers.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        
        # --- Data File Path ---
        # Construct a reliable path to the data file
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.data_file = os.path.join(project_root, 'data', 'semesters.json')

        self.semesters = self.load_data()
        self.selected_semester = None

        # --- UI Frames ---
        # Main frame for displaying semester buttons
        self.semester_display_frame = tk.Frame(self, bg="#f4f6f7")
        self.semester_display_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(self.semester_display_frame, text="Select a Semester", font=("Helvetica", 24, "bold"), bg="#f4f6f7", fg="#2c3e50").pack(pady=(20, 30))

        # This frame will hold the grid of buttons
        self.button_grid_frame = tk.Frame(self.semester_display_frame, bg="#f4f6f7")
        self.button_grid_frame.pack()

        # Developer-only frame
        self.dev_tools_frame = tk.Frame(self, bg="#e0e0e0", bd=2, relief=tk.GROOVE)

        self.setup_developer_tools()
        self.refresh_semester_buttons()

        # This event ensures the dev tools are shown/hidden when switching to this screen
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        """Called when the frame is raised to the top."""
        if self.controller.user_role == "developer":
            self.dev_tools_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        else:
            self.dev_tools_frame.pack_forget() # Hide the dev tools for regular users

    def load_data(self):
        """Loads semester data from the JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty/corrupt, create it with default data
            logging.warning(f"'{self.data_file}' not found or invalid. Creating with default data.")
            default_data = ["Semester 1", "Semester 2", "Semester 3"]
            self.save_data(default_data)
            return default_data

    def save_data(self, data):
        """Saves the given data to the JSON file."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True) # Ensure data dir exists
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Semester data saved to '{self.data_file}'")

    def refresh_semester_buttons(self):
        """Clears and re-creates the semester buttons from the data."""
        for widget in self.button_grid_frame.winfo_children():
            widget.destroy()

        for i, semester_name in enumerate(self.semesters):
            button = tk.Button(
                self.button_grid_frame,
                text=semester_name,
                font=("Helvetica", 14),
                width=15,
                pady=15,
                command=lambda s=semester_name: self.select_semester(s)
            )
            # Position button in a grid
            row, col = divmod(i, 4) # 4 buttons per row
            button.grid(row=row, column=col, padx=10, pady=10)

        self.selected_semester = None # Reset selection after refresh

    def select_semester(self, semester_name):
        """Handles a click on a semester button."""
        if self.controller.user_role == 'developer':
            self.selected_semester = semester_name
            messagebox.showinfo("Semester Selected", f"'{semester_name}' is selected for removal.", parent=self)
        else:
            # For a normal user, proceed to the next step
            messagebox.showinfo("Action", f"Proceeding to '{semester_name}'...", parent=self)
            # Future: self.controller.show_frame("LevelScreen")

    def setup_developer_tools(self):
        """Creates the widgets for the developer tools frame."""
        tk.Label(self.dev_tools_frame, text="Developer Tools", font=("Helvetica", 14, "bold"), bg="#e0e0e0").pack(pady=5)
        
        # --- Add Semester ---
        add_frame = tk.Frame(self.dev_tools_frame, bg="#e0e0e0")
        add_frame.pack(pady=5, padx=10)
        self.new_semester_entry = tk.Entry(add_frame, font=("Helvetica", 12), width=30)
        self.new_semester_entry.pack(side="left", ipady=4)
        tk.Button(add_frame, text="Add Semester", command=self.add_semester).pack(side="left", padx=10)

        # --- Remove Semester ---
        tk.Button(self.dev_tools_frame, text="Remove Selected Semester", command=self.remove_semester).pack(pady=10)

    def add_semester(self):
        """Adds a new semester from the entry field."""
        new_name = self.new_semester_entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Semester name cannot be empty.", parent=self)
            return
        if new_name in self.semesters:
            messagebox.showerror("Error", "This semester already exists.", parent=self)
            return

        self.semesters.append(new_name)
        self.save_data(self.semesters)
        self.refresh_semester_buttons()
        self.new_semester_entry.delete(0, 'end')
        logging.info(f"Developer added new semester: '{new_name}'")

    def remove_semester(self):
        """Removes the currently selected semester."""
        if not self.selected_semester:
            messagebox.showerror("Error", "No semester selected for removal.", parent=self)
            return

        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{self.selected_semester}'?"):
            self.semesters.remove(self.selected_semester)
            self.save_data(self.semesters)
            self.refresh_semester_buttons()
            logging.info(f"Developer removed semester: '{self.selected_semester}'")
            self.selected_semester = None




import tkinter as tk
import logging
import os

from ui.welcome import WelcomeWindow
from ui.role_selection import RoleSelectionScreen
from ui.semester import SemesterScreen # <-- IMPORT THE NEW SCREEN

# (Your logging setup remains the same)
# ... (logging code here) ...

# Add the new screen to the dictionary
SCREENS = {
    "WelcomeWindow": WelcomeWindow,
    "RoleSelectionScreen": RoleSelectionScreen,
    "SemesterScreen": SemesterScreen, # <-- ADD THIS LINE
}

class LearningRoboticsApp(tk.Tk):
    # (The __init__ method remains the same)
    # ...
    def show_frame(self, frame_name):
        """ Raises a given frame to the top to make it visible. """
        frame = self.frames[frame_name]
        # --- IMPORTANT: Notify the frame it's being shown ---
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
        logging.info(f"Switched view to {frame_name}.")
    # (The rest of the class remains the same)
    # ...

# (The `if __name__ == "__main__":` block remains the same)
# ...