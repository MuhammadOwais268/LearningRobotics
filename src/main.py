import tkinter as tk
import logging
import os

# --- We only import the screen we want to show ---
from ui.welcome import WelcomeWindow

# --- Your professional logging setup (no changes needed) ---
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class LearningRoboticsApp(tk.Tk):
    """
    The main application class. For now, its only job is to create and
    display the WelcomeWindow.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Learning Robotics")
        self.geometry("800x600")

        # --- Create the WelcomeWindow instance directly ---
        # We pass 'self' as both the parent container and the controller.
        # This satisfies the __init__(self, parent, controller) requirements
        # of the WelcomeWindow class.
        welcome_frame = WelcomeWindow(self, self)
        welcome_frame.pack(side="top", fill="both", expand=True)

    def show_frame(self, frame_name):
        """
        This method is required by WelcomeWindow's "Continue" button.
        Since there are no other screens, we can have it close the app
        or simply log a message.
        """
        logging.info(f"Transition requested to '{frame_name}'. Closing application as it's the only screen.")
        # When you add more screens, you will replace self.destroy() with the
        # logic to show the next frame.
        self.destroy()


if __name__ == "__main__":
    logging.info("Starting application from main.py (Welcome Screen only).")
    app = LearningRoboticsApp()
    app.mainloop()
    logging.info("Application closed.")