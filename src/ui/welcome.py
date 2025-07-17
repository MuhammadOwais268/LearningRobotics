import tkinter as tk
import os
import logging
# We need the Pillow library (PIL) for advanced image manipulation
try:
    from PIL import ImageTk, Image
except ImportError:
    logging.critical("Pillow library not found! Please run 'pip install Pillow'.")
    exit()

class WelcomeWindow(tk.Frame):
    """
    A professional, visually engaging welcome screen with dark text on a
    light, watermarked background image.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- 1. Setup Background ---
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            image_path = os.path.join(project_root, 'assets', 'robot.jpg')
            self.original_image = Image.open(image_path).convert("RGBA")
        except Exception as e:
            self.original_image = None
            logging.error(f"Fatal: Could not load background image. Error: {e}")

        # Bind the resizing function to the frame's <Configure> event
        self.bind("<Configure>", self._resize_background)

        # --- 2. Central Content Frame (Transparent) ---
        content_frame = tk.Frame(self)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # This makes the frame background transparent
        content_frame.configure(bg=self.cget('bg'))


        # --- 3. Create Widgets with DARK Text ---
        # By setting the fg (foreground) to a dark color, the text will be dark.
        
        # Welcome text animation
        self.welcome_label = tk.Label(content_frame, text="", font=("Helvetica", 64, "bold"), fg="#2c3e50") # Dark Blue/Gray
        self.welcome_label.pack(pady=(0, 25))

        # Subtitle
        self.subtitle = tk.Label(content_frame, text="The Developer of the Future Starts Here", font=("Helvetica", 18), fg="#34495e") # Slightly lighter dark blue/gray
        self.subtitle.pack(pady=(0, 50))

        # Make the label backgrounds transparent
        self.welcome_label.configure(bg=content_frame.cget('bg'))
        self.subtitle.configure(bg=content_frame.cget('bg'))

        # Continue Button with a modern look
        self.continue_btn = tk.Button(
            content_frame, text="Continue ➜", font=("Helvetica", 16, "bold"),
            fg="white", bg="#3498db", activeforeground="white",
            activebackground="#2980b9", relief=tk.FLAT, cursor="hand2",
            padx=25, pady=12, command=self.goto_next
        )
        self.continue_btn.pack()

        # --- 4. Start the text animation ---
        self.full_text = "Welcome!"
        self.current_index = 0
        self.after(500, self.animate_text)

    def _resize_background(self, event):
        """Dynamically resizes and creates a light watermark from the background image."""
        if not self.original_image:
            return

        win_width = event.width
        win_height = event.height
        
        # Resize the image to "cover" the window without distortion
        img_copy = self.original_image.copy()
        img_aspect = img_copy.width / img_copy.height
        win_aspect = win_width / win_height
        
        if win_aspect > img_aspect:
            new_height = int(win_width / img_aspect)
            img_copy = img_copy.resize((win_width, new_height), Image.Resampling.LANCZOS)
        else:
            new_width = int(win_height * img_aspect)
            img_copy = img_copy.resize((new_width, win_height), Image.Resampling.LANCZOS)
        
        img_copy = img_copy.crop(((img_copy.width - win_width) // 2,
                                  (img_copy.height - win_height) // 2,
                                  (img_copy.width + win_width) // 2,
                                  (img_copy.height + win_height) // 2))

        # --- THIS IS THE KEY TO THE WATERMARK EFFECT ---
        # Create a solid white layer
        white_layer = Image.new('RGBA', img_copy.size, (255, 255, 255, 255))
        # Blend the white layer with the robot image. alpha=0.85 means it's
        # 85% white and only 15% robot image, creating a faint watermark.
        watermarked_image = Image.blend(white_layer, img_copy, alpha=0.15)
        # --- END OF KEY ---

        self.bg_image_tk = ImageTk.PhotoImage(watermarked_image)
        self.bg_label.config(image=self.bg_image_tk)

    def animate_text(self):
        """Animates the welcome text."""
        if self.current_index < len(self.full_text):
            self.welcome_label.config(text=self.welcome_label.cget("text") + self.full_text[self.current_index])
            self.current_index += 1
            self.after(120, self.animate_text)

    # Inside the WelcomeWindow class in src/ui/welcome.py

    def goto_next(self):
        """Uses the main controller to switch to the RoleSelectionScreen."""
        logging.info("Welcome screen finished. Navigating to role selection.")
        # THE ONLY CHANGE IS HERE:
        self.controller.show_frame("RoleSelectionScreen")