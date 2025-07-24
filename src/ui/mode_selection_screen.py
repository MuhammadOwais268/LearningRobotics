# File: client/src/ui/mode_selection_screen.py (Corrected Version)

import tkinter as tk
from tkinter import simpledialog, messagebox

class ModeSelectionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        
        self.header_label = tk.Label(self, text="Select Your Mode", font=("Helvetica", 24, "bold"), bg="#f4f6f7")
        self.header_label.pack(pady=(40, 20))
        self.welcome_label = tk.Label(self, text="", font=("Helvetica", 12), bg="#f4f6f7")
        self.welcome_label.pack(pady=(0, 30))
        self.manage_class_button = tk.Button(self, text="Create / Manage a Class", font=("Helvetica", 14), command=self.manage_class)
        self.join_class_button = tk.Button(self, text="Join a Class", font=("Helvetica", 14), command=self.join_class)
        self.offline_button = tk.Button(self, text="Work Offline", font=("Helvetica", 14), command=self.work_offline)
        tk.Button(self, text="← Back to Login", command=self.controller.logout).pack(pady=(30,0))
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event=None):
        self.manage_class_button.pack_forget(); self.join_class_button.pack_forget(); self.offline_button.pack_forget()
        email = "User"
        if self.controller.current_user: email = self.controller.current_user.get('email', 'User')
        self.welcome_label.config(text=f"Logged in as: {email}")
        role = ""
        if self.controller.current_user: role = self.controller.current_user.get("role")
        if role == "developer": self.manage_class_button.pack(pady=10, ipady=8, fill='x', padx=100)
        else: self.join_class_button.pack(pady=10, ipady=8, fill='x', padx=100)
        self.offline_button.pack(pady=10, ipady=8, fill='x', padx=100)

    def manage_class(self):
        class_code = simpledialog.askstring("Manage Class", "Enter your Class Code to manage it.\nLeave blank to create a new class.")
        if class_code is not None:
            if class_code == "": self.controller.set_online_mode(is_new_class=True)
            else: self.controller.set_online_mode(class_code=class_code)

    def join_class(self):
        class_code = simpledialog.askstring("Join Class", "Enter the Class Code provided by your instructor:")
        if class_code: self.controller.set_online_mode(class_code=class_code)

    def work_offline(self):
        self.controller.set_offline_mode()