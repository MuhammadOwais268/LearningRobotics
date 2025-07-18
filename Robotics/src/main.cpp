# File: /home/owais/LearningRobotics/src/main.py
import tkinter as tk
import logging
import os
import json

from ui.welcome import WelcomeWindow
from ui.role_selection import RoleSelectionScreen
from ui.semester import SemesterScreen
from ui.level import LevelScreen
from ui.concept import ConceptScreen
from ui.implementation import ImplementationScreen

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCREENS = {
    "WelcomeWindow": WelcomeWindow,
    "RoleSelectionScreen": RoleSelectionScreen,
    "SemesterScreen": SemesterScreen,
    "LevelScreen": LevelScreen,
    "ConceptScreen": ConceptScreen,
    "ImplementationScreen": ImplementationScreen,
}

class LearningRoboticsApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Learning Robotics")
        self.geometry("900x700")

        self.user_role = None
        self.current_semester = None
        self.current_level = None
        
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(project_root, '..', 'data', 'learning_data.json')
        self.app_data = self.get_data()

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
        logging.info(f"Attempting to switch view to {frame_name}.")
        frame = self.frames[frame_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
        logging.info(f"Successfully switched view to {frame_name}.")
    
    def set_user_role(self, role):
        self.user_role = role
        logging.info(f"User role set to: '{role}'")

    def set_current_semester(self, semester_name):
        self.current_semester = semester_name
        logging.info(f"Current semester set to: '{semester_name}'")

    def set_current_selection(self, level=None):
        if level: 
            self.current_level = level
            logging.info(f"Current level set to: '{level}'")

    def get_data(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            default_data = {
                "Fall Semester 2025": {
                    "levels": {
                        "First Level": {
                            "description": "An example level.",
                            "concept": {"explanation": "Concept explanation...", "code": "// Concept code...", "output": ""},
                            "implementation": {"explanation": "Implementation explanation...", "code": "// Implementation code..."}
                        }
                    }
                }
            }
            self.save_data(default_data)
            return default_data

    def save_data(self, data):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        self.app_data = data
        logging.info(f"Data saved to '{self.data_file}'")

if __name__ == "__main__":
    logging.info("Starting application.")
    app = LearningRoboticsApp()
    app.mainloop()
    logging.info("Application closed.")