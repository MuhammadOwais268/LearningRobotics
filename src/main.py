# File: client/src/main.py (Complete Updated Version)

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
from .ui.dashboard_screen import DashboardScreen

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
    "DashboardScreen": DashboardScreen,
}

class LearningRoboticsApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Learning Robotics")
        self.geometry("1100x750")

        self.current_user = None; self.is_online = False; self.current_class_code = None
        self.network_client = NetworkClient(self); self.app_data = {}; self.library_file_to_view = None
        
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.local_data_file = os.path.join(self.project_root, '..', 'data', 'learning_data.json')
        self.robotics_project_path = os.path.join(self.project_root, 'Robotics')
        self.user_progress_file = os.path.join(self.project_root, '..', 'data', 'user_progress.json')

        container = tk.Frame(self); container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1); container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F_name, F_class in SCREENS.items():
            frame = F_class(container, self)
            self.frames[F_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("WelcomeWindow")

    # --- Progress Tracking Methods ---
    def _get_user_progress_data(self):
        try:
            with open(self.user_progress_file, 'r') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {}

    def _save_user_progress_data(self, progress_data):
        os.makedirs(os.path.dirname(self.user_progress_file), exist_ok=True)
        with open(self.user_progress_file, 'w') as f: json.dump(progress_data, f, indent=4)

    def get_current_user_progress(self):
        if not self.current_user: return {}
        all_progress = self._get_user_progress_data()
        user_email = self.current_user['email']
        return all_progress.get(user_email, {})

    # In client/src/main.py inside the LearningRoboticsApp class

    def save_last_viewed(self, semester, level, screen_type):
        """Saves the last location AND adds the level to a 'visited' list."""
        if not self.current_user or not semester or not level:
            return
            
        all_progress = self._get_user_progress_data()
        user_email = self.current_user['email']
        
        # --- FIX IS HERE ---
        # Get the user's data. If the user doesn't exist, create a complete
        # default structure for them.
        user_data = all_progress.setdefault(user_email, {
            "last_viewed": {}, 
            "completed_levels": [],
            "visited_levels": [] 
        })
        
        # Now, ensure all keys exist within the user's data, which is crucial
        # for migrating data from older versions of the app.
        user_data.setdefault("last_viewed", {})
        user_data.setdefault("completed_levels", [])
        user_data.setdefault("visited_levels", [])
        
        # --- END OF FIX ---

        # Now we can safely access all keys
        user_data['last_viewed'] = {
            "semester": semester, "level": level, "type": screen_type
        }
        level_id = f"{semester}/{level}"
        if level_id not in user_data['visited_levels']:
            user_data['visited_levels'].append(level_id)
        
        self._save_user_progress_data(all_progress)
        logging.info(f"Saved progress for {user_email}: Last viewed {level}")

    def mark_level_as_completed(self, semester, level):
        """Adds a level to the user's list of completed levels."""
        if not self.current_user or not semester or not level:
            return

        all_progress = self._get_user_progress_data()
        user_email = self.current_user['email']
        
        # --- FIX IS HERE (Same logic as above for robustness) ---
        user_data = all_progress.setdefault(user_email, {
            "last_viewed": {}, 
            "completed_levels": [],
            "visited_levels": [] 
        })
        user_data.setdefault("completed_levels", [])
        # --- END OF FIX ---
        
        level_id = f"{semester}/{level}"
        if level_id not in user_data['completed_levels']:
            user_data['completed_levels'].append(level_id)
            self._save_user_progress_data(all_progress)
            logging.info(f"Marked level as complete for {user_email}: {level_id}")

    def get_ordered_level_ids(self):
        level_ids = []
        # Use self.app_data which is already loaded
        for semester_name, semester_data in sorted(self.app_data.items()):
            for level_name in sorted(semester_data.get("levels", {}).keys()):
                level_ids.append(f"{semester_name}/{level_name}")
        return level_ids
    
    # --- Navigation Methods ---
    def set_online_mode(self, class_code=None, is_new_class=False):
        self.is_online = True
        if is_new_class:
            self.app_data = self._get_local_data()
            response = self.network_client.create_class(self.app_data)
            if response and response.get("success"):
                self.current_class_code = response.get("class_code")
                messagebox.showinfo("Class Created", f"New class created! Your Class Code is: {self.current_class_code}")
                self.network_client.start_live_feed()
                self.show_frame("DashboardScreen") 
            else:
                messagebox.showerror("Error", f"Could not create class: {response.get('message')}")
                self.is_online = False
        elif class_code:
            self.current_class_code = class_code
            self.network_client.start_live_feed()
            self.get_data() # Load the curriculum data first
            self.show_frame("DashboardScreen")

    def set_offline_mode(self):
        self.is_online = False; self.current_class_code = None; self.network_client.stop_live_feed()
        self.get_data() # Load curriculum data BEFORE showing dashboard
        self.show_frame("DashboardScreen")
    
    def show_frame(self, frame_name):
        logging.info(f"Switching view to {frame_name}.")
        frame = self.frames[frame_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()

    def get_robotics_project_path(self): return self.robotics_project_path
    
    def on_login_success(self, user_data):
        self.current_user = user_data
        logging.info(f"Login success. User: {self.current_user['email']}, Role: {self.current_user['role']}")
        self.show_frame("ModeSelectionScreen")
        
    def logout(self):
        self.current_user = None; self.is_online = False; self.current_class_code = None
        self.network_client.logout_user(); self.app_data = {}; self.show_frame("LoginScreen")
        
    def get_data(self):
        if self.is_online:
            if not self.current_class_code: self.app_data = {}; return self.app_data
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
    # In client/src/main.py inside the LearningRoboticsApp class

    def reset_current_user_progress(self):
        """
        Finds the current user in the progress file and resets their data
        to a blank state.
        """
        if not self.current_user:
            return

        all_progress = self._get_user_progress_data()
        user_email = self.current_user['email']
        
        # Check if the user exists in the progress file
        if user_email in all_progress:
            # Reset their data to the default empty structure
            all_progress[user_email] = {
                "last_viewed": {},
                "completed_levels": [],
                "visited_levels": []
            }
            self._save_user_progress_data(all_progress)
            logging.info(f"Progress has been reset for user {user_email}.")
            messagebox.showinfo("Progress Reset", "Your learning history and progress have been successfully reset.")
        else:
            # If they had no progress, there's nothing to reset.
            messagebox.showinfo("No Progress", "You had no progress saved, so there is nothing to reset.")
if __name__ == "__main__":
     app = LearningRoboticsApp()
     app.mainloop()