import tkinter as tk
from tkinter import messagebox

class SignupScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller

        # Main container for card-like effect
        card_frame = tk.Frame(self, bg="#ffffff", bd=2, relief="flat")
        card_frame.pack(pady=40, padx=20, fill="both", expand=True)

        # Input container for centering
        input_frame = tk.Frame(card_frame, bg="#ffffff")
        input_frame.pack(expand=True)

        # Sign Up Button
        self.signup_button = tk.Button(
            input_frame, 
            text="Sign Up", 
            font=("Helvetica", 12, "bold"), 
            bg="#3498db", 
            fg="white", 
            bd=0, 
            relief="flat",
            activebackground="#2980b9",
            command=self.perform_signup
        )
        self.signup_button.pack(pady=(0, 15), ipady=5)
        self.signup_button.bind("<Enter>", lambda e: self.signup_button.config(bg="#2980b9"))
        self.signup_button.bind("<Leave>", lambda e: self.signup_button.config(bg="#3498db"))

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

        # Developer Checkbox
        self.is_dev_var = tk.BooleanVar()
        self.dev_checkbox = tk.Checkbutton(
            input_frame, 
            text="Sign up as a Developer", 
            variable=self.is_dev_var, 
            command=self.toggle_dev_key, 
            font=("Helvetica", 14), 
            bg="#ffffff", 
            fg="#34495e", 
            activebackground="#ffffff"
        )
        self.dev_checkbox.pack(pady=8, anchor="center")

        # Developer Secret Key
        self.dev_key_label = tk.Label(
            input_frame, 
            text="Developer Secret Key", 
            font=("Helvetica", 14), 
            bg="#ffffff", 
            fg="#34495e"
        )
        self.dev_key_entry = tk.Entry(
            input_frame, 
            show="*", 
            width=30, 
            font=("Helvetica", 14), 
            bd=1, 
            relief="solid", 
            bg="#f9f9f9"
        )
        self.dev_key_entry.insert(0, "Developer Key")
        self.dev_key_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.dev_key_entry, "Developer Key"))
        self.dev_key_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.dev_key_entry, "Developer Key"))

        # Back to Login Link
        login_frame = tk.Frame(card_frame, bg="#ffffff")
        login_frame.pack(pady=15)
        tk.Label(
            login_frame, 
            text="Already have an account?", 
            font=("Helvetica", 12), 
            bg="#ffffff", 
            fg="#7f8c8d"
        ).pack(side="left")
        login_button = tk.Button(
            login_frame, 
            text="Log In", 
            font=("Helvetica", 12, "underline"), 
            bg="#ffffff", 
            fg="#3498db", 
            bd=0, 
            command=lambda: self.controller.show_frame("LoginScreen")
        )
        login_button.pack(side="left", padx=5)
        login_button.bind("<Enter>", lambda e: login_button.config(fg="#2980b9"))
        login_button.bind("<Leave>", lambda e: login_button.config(fg="#3498db"))

        # Initial state for dev key fields
        self.toggle_dev_key()

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if placeholder == "Password" or placeholder == "Developer Key":
                entry.config(show="*")

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            if placeholder == "Password" or placeholder == "Developer Key":
                entry.config(show="")

    def toggle_dev_key(self):
        if self.is_dev_var.get():
            self.dev_key_label.pack(pady=(10, 5), anchor="center")
            self.dev_key_entry.pack(pady=5, anchor="center")
        else:
            self.dev_key_label.pack_forget()
            self.dev_key_entry.pack_forget()
    
    def perform_signup(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = "developer" if self.is_dev_var.get() else "student"
        dev_key = self.dev_key_entry.get() if self.is_dev_var.get() else None

        if not email or not password or email == "Email" or password == "Password" or (self.is_dev_var.get() and dev_key == "Developer Key"):
            messagebox.showerror("Error", "Please enter valid email, password, and developer key (if applicable).")
            return

        response = self.controller.network_client.signup_user(email, password, role, dev_key)
        if response and response.get("success"):
            messagebox.showinfo("Success", "Account created successfully! Please log in.")
            self.controller.show_frame("LoginScreen")
        else:
            messagebox.showerror("Signup Failed", response.get("message", "An unknown error occurred."))