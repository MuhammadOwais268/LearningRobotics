# File: client/src/main.py (Final Version)

import tkinter as tk
from tkinter import messagebox
import logging
import os
import json

from .network_client import NetworkClient
from .ui.welcome import WelcomeWindow
from .ui.signup_screen import SignupScreen
from .ui.login_screen import LoginScreen
from .ui.mode_selection_screen import ModeSelectionScreen
from .ui.semester import SemesterScreen
from .ui.level import LevelScreen
from .ui.concept import ConceptScreen
from .ui.implementation import ImplementationScreen
from .ui.library_viewer_screen import LibraryViewerScreen

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCREENS = {
    "WelcomeWindow": WelcomeWindow,
    "SignupScreen": SignupScreen,
    "LoginScreen": LoginScreen,
    "ModeSelectionScreen": ModeSelectionScreen,
    "SemesterScreen": SemesterScreen,
    "LevelScreen": LevelScreen,
    "ConceptScreen": ConceptScreen,
    "ImplementationScreen": ImplementationScreen,
    "LibraryViewerScreen": LibraryViewerScreen,
}

class LearningRoboticsApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Learning Robotics")
        self.geometry("1100x750")

        # --- State Management ---
        self.current_user = None
        self.is_online = False
        self.current_class_code = None
        self.network_client = NetworkClient(self)
        self.app_data = {}
        self.library_file_to_view = None

        # --- Path Management ---
        # project_root is .../LearningRobotics/src/
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.local_data_file = os.path.join(self.project_root, '..', 'data', 'learning_data.json')
        # The permanent PlatformIO project folder
        self.robotics_project_path = os.path.join(self.project_root, 'Robotics')

        # --- UI Container Setup ---
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
        logging.info(f"Switching view to {frame_name}.")
        frame = self.frames[frame_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()

    def get_robotics_project_path(self):
        """Provides a reliable path to the permanent 'Robotics' project folder."""
        return self.robotics_project_path

    # ... (Rest of the methods are unchanged and correct) ...
    def on_login_success(self, user_data):
        self.current_user = user_data
        logging.info(f"Login success. User: {self.current_user['email']}, Role: {self.current_user['role']}")
        self.show_frame("ModeSelectionScreen")
    def set_online_mode(self, class_code=None, is_new_class=False):
        self.is_online = True
        if is_new_class:
            local_data = self._get_local_data()
            response = self.network_client.create_class(local_data)
            if response and response.get("success"):
                self.current_class_code = response.get("class_code")
                self.app_data = local_data
                messagebox.showinfo("Class Created", f"New class created! Your Class Code is: {self.current_class_code}")
                self.network_client.start_live_feed()
                self.show_frame("SemesterScreen")
            else:
                messagebox.showerror("Error", f"Could not create class: {response.get('message')}")
                self.is_online = False
        elif class_code:
            self.current_class_code = class_code
            self.network_client.start_live_feed()
            self.show_frame("SemesterScreen")
    def set_offline_mode(self):
        self.is_online = False
        self.current_class_code = None
        self.network_client.stop_live_feed()
        self.show_frame("SemesterScreen")
    def logout(self):
        self.current_user = None; self.is_online = False; self.current_class_code = None
        self.network_client.logout_user(); self.app_data = {}; self.show_frame("LoginScreen")
    def get_data(self):
        if self.is_online:
            response = self.network_client.get_class_data(self.current_class_code)
            if response and response.get("success"): self.app_data = response.get("curriculum", {})
            else: messagebox.showerror("Error", f"Failed to fetch class data: {response.get('message')}"); self.app_data = {}
        else: self.app_data = self._get_local_data()
        return self.app_data
    def save_data(self, data_to_save):
        self.app_data = data_to_save
        if self.is_online:
            if self.current_user.get('role') != 'developer': return
            response = self.network_client.update_class_data(self.current_class_code, self.app_data)
            if not response or not response.get("success"): messagebox.showerror("Error", f"Failed to save data to server: {response.get('message')}")
        else: self._save_local_data(self.app_data)
    def _get_local_data(self):
        try:
            with open(self.local_data_file, 'r') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {"Default Semester (Offline)": {"levels": {}}}
    def _save_local_data(self, data):
        os.makedirs(os.path.dirname(self.local_data_file), exist_ok=True)
        with open(self.local_data_file, 'w') as f: json.dump(data, f, indent=4)
    def update_student_count_display(self, count):
        semester_screen = self.frames.get("SemesterScreen")
        if semester_screen: semester_screen.update_student_count(count)

if __name__ == "__main__":
     app = LearningRoboticsApp()
     app.mainloop()