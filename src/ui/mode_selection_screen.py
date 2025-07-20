# File: src/ui/mode_selection_screen.py

import tkinter as tk
from tkinter import simpledialog, messagebox

class ModeSelectionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.header_label = tk.Label(self, text="Select Your Mode", font=("Helvetica", 18, "bold"))
        self.header_label.pack(pady=(20, 10))

        self.welcome_label = tk.Label(self, text="", font=("Helvetica", 11))
        self.welcome_label.pack(pady=(0, 20))
        
        self.create_class_button = tk.Button(self, text="Create / Manage a Class", command=self.manage_class)
        self.join_class_button = tk.Button(self, text="Join a Class", command=self.join_class)
        self.offline_button = tk.Button(self, text="Work Offline", command=self.work_offline)
        self.logout_button = tk.Button(self, text="Logout", fg="red", command=self.controller.logout)


        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event=None):
        """Dynamically display buttons based on the user's role."""
        self.create_class_button.pack_forget()
        self.join_class_button.pack_forget()
        self.offline_button.pack_forget()
        self.logout_button.pack_forget()

        email = self.controller.current_user.get('email', 'User')
        self.welcome_label.config(text=f"Logged in as: {email}")

        role = self.controller.current_user.get("role")
        if role == "developer":
            self.create_class_button.pack(pady=10, ipady=8, fill='x', padx=50)
        else: # student
            self.join_class_button.pack(pady=10, ipady=8, fill='x', padx=50)
            
        self.offline_button.pack(pady=10, ipady=8, fill='x', padx=50)
        self.logout_button.pack(pady=(20, 10))

    def manage_class(self):
        class_code = simpledialog.askstring("Manage Class", "Enter your Class Code to manage it.\nLeave blank to create a new class.")
        if class_code is not None:
            if class_code == "":
                self.controller.set_online_mode(is_new_class=True)
            else:
                self.controller.set_online_mode(class_code=class_code)

    def join_class(self):
        class_code = simpledialog.askstring("Join Class", "Enter the Class Code:")
        if class_code:
            self.controller.set_online_mode(class_code=class_code)

    def work_offline(self):
        self.controller.set_offline_mode()