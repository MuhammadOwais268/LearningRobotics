import tkinter as tk
import logging

class RoleSelectionScreen(tk.Frame):
    """
    An authentication screen to determine if the user is a 'Developer' or 'User'.
    """
    DEVELOPER_USERNAME = "developer"
    DEVELOPER_PASSWORD = "password123"

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.configure(bg="#f4f6f7")

        login_frame = tk.Frame(self, bg="#f4f6f7")
        login_frame.pack(expand=True)

        title_label = tk.Label(
            login_frame, text="Authentication", font=("Helvetica", 32, "bold"),
            fg="#2c3e50", bg="#f4f6f7"
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(
            login_frame, text="Enter credentials to access developer mode.",
            font=("Helvetica", 12), fg="#34495e", bg="#f4f6f7"
        )
        subtitle_label.pack(pady=(0, 30))

        username_label = tk.Label(login_frame, text="Username", font=("Helvetica", 12), bg="#f4f6f7")
        username_label.pack(fill='x', padx=20)
        self.username_entry = tk.Entry(login_frame, font=("Helvetica", 14), bd=2, relief=tk.FLAT)
        self.username_entry.pack(pady=(0, 20), fill='x', padx=20, ipady=5)

        password_label = tk.Label(login_frame, text="Password", font=("Helvetica", 12), bg="#f4f6f7")
        password_label.pack(fill='x', padx=20)
        self.password_entry = tk.Entry(login_frame, font=("Helvetica", 14), bd=2, relief=tk.FLAT, show="*")
        self.password_entry.pack(pady=(0, 30), fill='x', padx=20, ipady=5)

        login_button = tk.Button(
            login_frame, text="Continue", font=("Helvetica", 14, "bold"),
            fg="white", bg="#3498db", activeforeground="white",
            activebackground="#2980b9", relief=tk.FLAT, cursor="hand2",
            command=self.attempt_login
        )
        login_button.pack(fill='x', padx=20, ipady=8)
        
        self.message_label = tk.Label(login_frame, text="", font=("Helvetica", 10), bg="#f4f6f7")
        self.message_label.pack(pady=(10, 0))

        # --- ADDED: Back button to return to the Welcome screen ---
        back_button = tk.Button(
            login_frame, text="← Back", font=("Helvetica", 10),
            fg="#34495e", bg="#f4f6f7", relief=tk.FLAT,
            cursor="hand2", command=self.go_back
        )
        back_button.pack(pady=(20, 0))

    def attempt_login(self):
        """
        Checks credentials and sets the role before proceeding to the SemesterScreen.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = "user"

        if username == self.DEVELOPER_USERNAME and password == self.DEVELOPER_PASSWORD:
            role = "developer"
            self.message_label.config(text="Developer login successful!", fg="green")
            logging.info("Correct developer credentials entered.")
        else:
            if username or password: 
                self.message_label.config(text="Invalid credentials. Proceeding as User.", fg="red")
            else:
                self.message_label.config(text="Proceeding as User.", fg="gray")
            logging.info("No/Invalid developer credentials. Defaulting to USER role.")
        
        self.controller.set_user_role(role)
        self.after(1000, lambda: self.controller.show_frame("SemesterScreen"))

    def go_back(self):
        """Navigates back to the WelcomeWindow screen."""
        logging.info("Navigating back from Role Selection to Welcome screen.")
        self.message_label.config(text="") # Clear any error messages
        self.controller.show_frame("WelcomeWindow")