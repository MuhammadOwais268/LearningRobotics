# File: src/ui/welcome.py

# ... (keep all existing code for PIL, os, logging, etc.) ...
import tkinter as tk
import os
import logging
try:
    from PIL import ImageTk, Image
except ImportError:
    logging.critical("Pillow library not found! Please run 'pip install Pillow'.")
    exit()

class WelcomeWindow(tk.Frame):
    # ... (keep the entire __init__ method as it is) ...
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- 1. Setup Background ---
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        try:
            # Adjust the path to go up two directories from src/ui to the project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            image_path = os.path.join(project_root, 'assets', 'robot.jpg') # Assuming assets folder is at the root
            self.original_image = Image.open(image_path).convert("RGBA")
        except Exception as e:
            self.original_image = None
            logging.error(f"Could not load background image from {image_path}. Error: {e}")

        # Bind the resizing function to the frame's <Configure> event
        self.bind("<Configure>", self._resize_background)

        # --- 2. Central Content Frame ---
        content_frame = tk.Frame(self, bg=self.cget('bg'))
        content_frame.place(relx=0.5, rely=0.5, anchor='center')

        # --- 3. Create Widgets ---
        self.welcome_label = tk.Label(content_frame, text="", font=("Helvetica", 64, "bold"), fg="#2c3e50", bg=content_frame.cget('bg'))
        self.welcome_label.pack(pady=(0, 25))

        self.subtitle = tk.Label(content_frame, text="The Developer of the Future Starts Here", font=("Helvetica", 18), fg="#34495e", bg=content_frame.cget('bg'))
        self.subtitle.pack(pady=(0, 50))

        self.continue_btn = tk.Button(
            content_frame, text="Continue ➜", font=("Helvetica", 16, "bold"),
            fg="white", bg="#3498db", activeforeground="white",
            activebackground="#2980b9", relief=tk.FLAT, cursor="hand2",
            padx=25, pady=12, command=self.goto_next
        )
        self.continue_btn.pack()

        # --- 4. Start Animation ---
        self.full_text = "Welcome!"
        self.current_index = 0
        self.after(500, self.animate_text)

    def _resize_background(self, event):
        # ... (keep this method exactly as it is) ...
        if not self.original_image: return
        win_width, win_height = event.width, event.height
        img_copy = self.original_image.copy()
        img_aspect = img_copy.width / img_copy.height
        win_aspect = win_width / win_height
        
        if win_aspect > img_aspect:
            new_height = int(win_width / img_aspect)
            img_copy = img_copy.resize((win_width, new_height), Image.Resampling.LANCZOS)
        else:
            new_width = int(win_height * img_aspect)
            img_copy = img_copy.resize((new_width, win_height), Image.Resampling.LANCZOS)
        
        img_copy = img_copy.crop(((img_copy.width - win_width) // 2, (img_copy.height - win_height) // 2, (img_copy.width + win_width) // 2, (img_copy.height + win_height) // 2))
        white_layer = Image.new('RGBA', img_copy.size, (255, 255, 255, 255))
        watermarked_image = Image.blend(white_layer, img_copy, alpha=0.15)
        self.bg_image_tk = ImageTk.PhotoImage(watermarked_image)
        self.bg_label.config(image=self.bg_image_tk)

    def animate_text(self):
        # ... (keep this method exactly as it is) ...
        if self.current_index < len(self.full_text):
            self.welcome_label.config(text=self.welcome_label.cget("text") + self.full_text[self.current_index])
            self.current_index += 1
            self.after(120, self.animate_text)

    def goto_next(self):
        """ <<<< MODIFIED PART >>>> """
        # Navigate to the new Login Screen instead of the old role selection.
        logging.info("Welcome screen finished. Navigating to login.")
        self.controller.show_frame("LoginScreen")