# File: src/ui/login_screen.py
import tkinter as tk
from tkinter import messagebox

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="Login", font=("Helvetica", 18, "bold")).pack(pady=20)
        
        tk.Label(self, text="Email:").pack(padx=20, anchor='w')
        self.email_entry = tk.Entry(self, width=40)
        self.email_entry.pack(padx=20, pady=5, fill='x')

        tk.Label(self, text="Password:").pack(padx=20, anchor='w')
        self.password_entry = tk.Entry(self, show="*", width=40)
        self.password_entry.pack(padx=20, pady=5, fill='x')

        tk.Button(self, text="Login", command=self.perform_login).pack(pady=20, ipady=5, fill='x', padx=20)
        
        tk.Label(self, text="Don't have an account?").pack()
        tk.Button(self, text="Sign Up", command=lambda: self.controller.show_frame("SignupScreen")).pack()

    def perform_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password.")
            return

        response = self.controller.network_client.login_user(email, password)
        if response and response.get("success"):
            user_data = {"email": email, "role": response.get("role")}
            self.controller.on_login_success(user_data)
        else:
            messagebox.showerror("Login Failed", response.get("message", "Invalid credentials or network error."))