import tkinter as tk
from tkinter import messagebox

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller

        # Main container for card-like effect
        card_frame = tk.Frame(self, bg="#ffffff", bd=2, relief="flat")
        card_frame.pack(pady=40, padx=20, fill="both", expand=True)

        # Input container for centering
        input_frame = tk.Frame(card_frame, bg="#ffffff")
        input_frame.pack(expand=True)

        # Login Button
        self.login_button = tk.Button(
            input_frame, 
            text="Login", 
            font=("Helvetica", 12, "bold"), 
            bg="#3498db", 
            fg="white", 
            bd=0, 
            relief="flat",
            activebackground="#2980b9",
            command=self.perform_login
        )
        self.login_button.pack(pady=(0, 15), ipady=5)
        self.login_button.bind("<Enter>", lambda e: self.login_button.config(bg="#2980b9"))
        self.login_button.bind("<Leave>", lambda e: self.login_button.config(bg="#3498db"))

        # Email
        tk.Label(
            input_frame, 
            text="Email", 
            font=("Helvetica", 14), 
            bg="#ffffff", 
            fg="#34495e"
        ).pack(pady=(0, 5), anchor="center")
        self.email_entry = tk.Entry(
            input_frame, 
            width=30, 
            font=("Helvetica", 14), 
            bd=1, 
            relief="solid", 
            bg="#f9f9f9"
        )
        self.email_entry.insert(0, "Email")
        self.email_entry.pack(pady=5, anchor="center")
        self.email_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.email_entry, "Email"))
        self.email_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.email_entry, "Email"))

        # Password
        tk.Label(
            input_frame, 
            text="Password", 
            font=("Helvetica", 14), 
            bg="#ffffff", 
            fg="#34495e"
        ).pack(pady=(10, 5), anchor="center")
        self.password_entry = tk.Entry(
            input_frame, 
            show="*", 
            width=30, 
            font=("Helvetica", 14), 
            bd=1, 
            relief="solid", 
            bg="#f9f9f9"
        )
        self.password_entry.insert(0, "Password")
        self.password_entry.pack(pady=5, anchor="center")
        self.password_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.password_entry, "Password"))
        self.password_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.password_entry, "Password"))

        # Signup Link
        signup_frame = tk.Frame(card_frame, bg="#ffffff")
        signup_frame.pack(pady=15)
        tk.Label(
            signup_frame, 
            text="Don't have an account?", 
            font=("Helvetica", 12), 
            bg="#ffffff", 
            fg="#7f8c8d"
        ).pack(side="left")
        signup_button = tk.Button(
            signup_frame, 
            text="Sign Up", 
            font=("Helvetica", 12, "underline"), 
            bg="#ffffff", 
            fg="#3498db", 
            bd=0, 
            command=lambda: self.controller.show_frame("SignupScreen")
        )
        signup_button.pack(side="left", padx=5)
        signup_button.bind("<Enter>", lambda e: signup_button.config(fg="#2980b9"))
        signup_button.bind("<Leave>", lambda e: signup_button.config(fg="#3498db"))

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if placeholder == "Password":
                entry.config(show="*")

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            if placeholder == "Password":
                entry.config(show="")

    def perform_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if not email or not password or email == "Email" or password == "Password":
            messagebox.showerror("Error", "Please enter both email and password.")
            return

        response = self.controller.network_client.login_user(email, password)
        if response and response.get("success"):
            user_data = {"email": email, "role": response.get("role")}
            self.controller.on_login_success(user_data)
        else:
            messagebox.showerror("Login Failed", response.get("message", "Invalid credentials or network error."))