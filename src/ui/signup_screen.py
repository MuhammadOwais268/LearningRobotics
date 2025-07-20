# File: src/ui/signup_screen.py
import tkinter as tk
from tkinter import messagebox

class SignupScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="Create an Account", font=("Helvetica", 18, "bold")).pack(pady=20)
        
        tk.Label(self, text="Email:").pack(padx=20, anchor='w')
        self.email_entry = tk.Entry(self, width=40)
        self.email_entry.pack(padx=20, pady=5, fill='x')

        tk.Label(self, text="Password:").pack(padx=20, anchor='w')
        self.password_entry = tk.Entry(self, show="*", width=40)
        self.password_entry.pack(padx=20, pady=5, fill='x')

        self.is_dev_var = tk.BooleanVar()
        self.dev_checkbox = tk.Checkbutton(self, text="Sign up as a Developer", variable=self.is_dev_var, command=self.toggle_dev_key)
        self.dev_checkbox.pack(pady=10)

        self.dev_key_label = tk.Label(self, text="Developer Secret Key:")
        self.dev_key_entry = tk.Entry(self, show="*", width=40)

        tk.Button(self, text="Sign Up", command=self.perform_signup).pack(pady=20, ipady=5, fill='x', padx=20)
        tk.Button(self, text="Back to Login", command=lambda: self.controller.show_frame("LoginScreen")).pack()

    def toggle_dev_key(self):
        if self.is_dev_var.get():
            self.dev_key_label.pack(padx=20, anchor='w')
            self.dev_key_entry.pack(padx=20, pady=5, fill='x')
        else:
            self.dev_key_label.pack_forget()
            self.dev_key_entry.pack_forget()
    
    def perform_signup(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = "developer" if self.is_dev_var.get() else "student"
        dev_key = self.dev_key_entry.get() if self.is_dev_var.get() else None

        if not email or not password:
            messagebox.showerror("Error", "Email and Password are required.")
            return

        response = self.controller.network_client.signup_user(email, password, role, dev_key)
        if response and response.get("success"):
            messagebox.showinfo("Success", "Account created successfully! Please log in.")
            self.controller.show_frame("LoginScreen")
        else:
            messagebox.showerror("Signup Failed", response.get("message", "An unknown error occurred."))