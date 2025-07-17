import tkinter as tk
import logging
import os
import json

# --- Import ALL screen classes ---
from ui.welcome import WelcomeWindow
from ui.role_selection import RoleSelectionScreen
from ui.semester import SemesterScreen
from ui.level import LevelScreen # <-- IMPORT THE NEW SCREEN

# --- Logging setup (no changes) ---
# ... (copy your existing logging setup here) ...

# --- ADD THE NEW SCREEN TO THE DICTIONARY ---
SCREENS = {
    "WelcomeWindow": WelcomeWindow,
    "RoleSelectionScreen": RoleSelectionScreen,
    "SemesterScreen": SemesterScreen,
    "LevelScreen": LevelScreen, # <-- ADD THIS LINE
}

class LearningRoboticsApp(tk.Tk):
    """ The main application class that manages state and screen transitions. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Learning Robotics")
        self.geometry("800x600")

        # --- APPLICATION STATE ---
        self.user_role = None
        self.current_semester = None # <-- NEW: Store selected semester
        
        # --- NEW: Centralized Data Handling ---
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.data_file = os.path.join(project_root, 'data', 'learning_data.json')
        self.app_data = self.get_data()

        # ... (The rest of the __init__ method is the same) ...
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F_name, F_class in SCREENS.items():
            frame = F_class(container, self)
            self.frames[F_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeWindow")

    def show_frame(self, frame_name):
        # ... (This method is the same) ...
        frame = self.frames[frame_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
        logging.info(f"Switched view to {frame_name}.")
    
    def set_user_role(self, role):
        # ... (This method is the same) ...
        self.user_role = role

    # --- NEW METHODS FOR DATA AND STATE MANAGEMENT ---
    def set_current_semester(self, semester_name):
        """Sets the currently selected semester."""
        self.current_semester = semester_name
        logging.info(f"Current semester set to: '{semester_name}'")

    def get_data(self):
        """Loads learning data from the JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            default_data = {
                "Semester 1": {"levels": {"Input/Output Operations": {}, "Variables & Data Types": {}}},
                "Semester 2": {"levels": {}},
            }
            self.save_data(default_data)
            return default_data

    def save_data(self, data):
        """Saves data to the JSON file and reloads it."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        self.app_data = data # Ensure in-memory data is also updated
        logging.info(f"Data saved to '{self.data_file}'")

if __name__ == "__main__":
    logging.info("Starting application.")
    app = LearningRoboticsApp()
    app.mainloop()
    logging.info("Application closed.")