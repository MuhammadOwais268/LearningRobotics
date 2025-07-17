import tkinter as tk
import logging
import os

# --- Import ALL the screen classes your application will use ---
from ui.welcome import WelcomeWindow
from ui.role_selection import RoleSelectionScreen
from ui.semester import SemesterScreen # <-- IMPORT THE NEW SCREEN

# --- Your professional logging setup (no changes needed) ---
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')
logging.basicConfig(
    filename=log_file, level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


# --- THIS IS THE KEY FIX ---
# Add the SemesterScreen to the dictionary of known screens.
SCREENS = {
    "WelcomeWindow": WelcomeWindow,
    "RoleSelectionScreen": RoleSelectionScreen,
    "SemesterScreen": SemesterScreen, # <-- ADD THIS LINE
}

class LearningRoboticsApp(tk.Tk):
    """ The main application class that manages state and screen transitions. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Learning Robotics")
        self.geometry("800x600")
        self.user_role = None

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # This loop will now correctly create an instance of SemesterScreen
        # and add it to the self.frames dictionary.
        for F_name, F_class in SCREENS.items():
            frame = F_class(container, self)
            self.frames[F_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        logging.info("Application initialized. Showing WelcomeWindow.")
        self.show_frame("WelcomeWindow")

    def show_frame(self, frame_name):
        """ Raises a given frame to the top and notifies it. """
        if frame_name not in self.frames:
            logging.error(f"FATAL: Attempted to show non-existent frame '{frame_name}'.")
            return

        frame = self.frames[frame_name]
        # This event is crucial for our semester.py to show/hide the dev tools.
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
        logging.info(f"Switched view to {frame_name}.")
    
    def set_user_role(self, role):
        """ A dedicated method to set and log the user's role. """
        if role in ["user", "developer"]:
            self.user_role = role
        else:
            logging.warning(f"Attempted to set an invalid role: {role}")


if __name__ == "__main__":
    logging.info("Starting application from main.py")
    app = LearningRoboticsApp()
    app.mainloop()
    logging.info("Application closed.")