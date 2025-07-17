import tkinter as tk
import logging
import os
import json

# --- Import ALL screen classes ---
from ui.welcome import WelcomeWindow
from ui.role_selection import RoleSelectionScreen
from ui.semester import SemesterScreen
from ui.level import LevelScreen
from ui.concept import ConceptScreen

# --- Logging setup (no changes) ---
# ... (copy your existing logging setup here) ...

SCREENS = {
    "WelcomeWindow": WelcomeWindow, "RoleSelectionScreen": RoleSelectionScreen,
    "SemesterScreen": SemesterScreen, "LevelScreen": LevelScreen,
    "ConceptScreen": ConceptScreen,
}

class LearningRoboticsApp(tk.Tk):
    """ The main application class that manages state and screen transitions. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Learning Robotics")
        self.geometry("800x600")

        # --- APPLICATION STATE ---
        self.user_role = None
        self.current_semester = None
        self.current_level = None
        self.current_path = None
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.data_file = os.path.join(project_root, 'data', 'learning_data.json')
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
        frame = self.frames[frame_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
        logging.info(f"Switched view to {frame_name}.")
    
    def set_user_role(self, role):
        self.user_role = role

    def set_current_semester(self, semester_name):
        self.current_semester = semester_name
        logging.info(f"Current semester set to: '{semester_name}'")

    def set_current_selection(self, level=None, path=None):
        if level: self.current_level = level
        if path: self.current_path = path

    def get_data(self):
        """Loads learning data from the JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # --- THIS IS THE ONLY CHANGE: The new default data structure ---
            default_data = {
                "Semester 1": {
                    "levels": {
                        "Serial Printing": {
                            "description": "Learn to send data from the robot to your computer.",
                            "concept": {
                                "explanation": "The Serial Monitor is a tool for communication between your robot and computer. It's essential for debugging and viewing sensor data.",
                                "code": "// This is the basic command to print text.\nSerial.println(\"Your Message Here\");",
                                "output": "Your Message Here"
                            },
                            "implementation": {
                                "explanation": "This complete Arduino sketch initializes serial communication in setup() and repeatedly prints 'Hello, World!' in loop().",
                                "code": "void setup() {\n  // Start serial communication at 9600 bits per second:\n  Serial.begin(9600);\n}\n\nvoid loop() {\n  // Print data to the serial port with a new line:\n  Serial.println(\"Hello, World!\");\n  delay(1000); // Wait for a second\n}",
                                "output": "Hello, World!\nHello, World!\n(repeating every second)"
                            }
                        }
                    }
                }
            }
            self.save_data(default_data)
            return default_data

    def save_data(self, data):
        """Saves data to the JSON file and reloads it."""
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