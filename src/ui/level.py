import tkinter as tk
from tkinter import messagebox, Listbox, simpledialog
import logging

class LevelScreen(tk.Frame):
    """
    Displays the levels (topics) for a selected semester like a table of contents.
    Provides developer tools to add, edit, and remove levels.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        self.current_semester = None

        # --- Header Frame ---
        header_frame = tk.Frame(self, bg="#f4f6f7")
        header_frame.pack(pady=20, padx=20, fill="x")
        tk.Button(header_frame, text="← Back to Semesters", command=self.go_back).pack(side="left")
        self.title_label = tk.Label(header_frame, text="Levels", font=("Helvetica", 24, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self.title_label.pack(side="left", expand=True)

        # --- Content Frame (Table of Contents) ---
        content_frame = tk.Frame(self, bg="#f4f6f7")
        content_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.level_listbox = Listbox(content_frame, font=("Helvetica", 14), bd=0, highlightthickness=0)
        self.level_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=self.level_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.level_listbox.config(yscrollcommand=scrollbar.set)

        # --- Developer Tools Frame ---
        self.dev_tools_frame = tk.Frame(self, bg="#e0e0e0", bd=2, relief=tk.GROOVE)
        self.setup_developer_tools()

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        """Called when the frame is raised. Updates content for the current semester."""
        self.current_semester = self.controller.current_semester
        if not self.current_semester:
            logging.error("LevelScreen shown without a semester being set.")
            self.go_back()
            return
        
        self.title_label.config(text=f"Levels for {self.current_semester}")
        self.refresh_level_list()

        if self.controller.user_role == "developer":
            self.dev_tools_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        else:
            self.dev_tools_frame.pack_forget()

    def refresh_level_list(self):
        """Loads levels for the current semester and populates the listbox."""
        self.level_listbox.delete(0, 'end')
        levels = self.controller.get_data().get(self.current_semester, {}).get("levels", {})
        for level_name in levels:
            self.level_listbox.insert('end', level_name)

    def setup_developer_tools(self):
        """Creates the widgets for the developer panel."""
        tk.Label(self.dev_tools_frame, text="Developer Tools", font=("Helvetica", 14, "bold"), bg="#e0e0e0").pack()
        
        button_bar = tk.Frame(self.dev_tools_frame, bg="#e0e0e0")
        button_bar.pack(pady=10, fill='x', padx=10)
        
        tk.Button(button_bar, text="Add New Level", command=self.add_level).pack(side="left", expand=True, fill='x', padx=5)
        tk.Button(button_bar, text="Edit Selected", command=self.edit_level).pack(side="left", expand=True, fill='x', padx=5)
        tk.Button(button_bar, text="Remove Selected", command=self.remove_level, bg="#c0392b", fg="white").pack(side="left", expand=True, fill='x', padx=5)

    def add_level(self):
        """Opens a dialog to add a new level."""
        new_level = simpledialog.askstring("Add Level", "Enter the name for the new level:", parent=self)
        if not new_level or not new_level.strip():
            return

        data = self.controller.get_data()
        if new_level in data[self.current_semester]["levels"]:
            messagebox.showerror("Error", "A level with this name already exists.", parent=self)
            return
        
        data[self.current_semester]["levels"][new_level] = {} # Add new level with empty content
        self.controller.save_data(data)
        self.refresh_level_list()
        logging.info(f"Developer added level '{new_level}' to '{self.current_semester}'")

    def edit_level(self):
        """Opens a dialog to edit the selected level."""
        selected_index = self.level_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a level to edit.", parent=self)
            return
        
        old_name = self.level_listbox.get(selected_index)
        new_name = simpledialog.askstring("Edit Level", f"Enter the new name for '{old_name}':", initialvalue=old_name, parent=self)

        if not new_name or not new_name.strip() or new_name == old_name:
            return
            
        data = self.controller.get_data()
        if new_name in data[self.current_semester]["levels"]:
            messagebox.showerror("Error", "Another level with this name already exists.", parent=self)
            return
        
        # Re-create the level content under the new name and delete the old one
        data[self.current_semester]["levels"][new_name] = data[self.current_semester]["levels"].pop(old_name)
        self.controller.save_data(data)
        self.refresh_level_list()
        logging.info(f"Developer edited level '{old_name}' to '{new_name}' in '{self.current_semester}'")

    def remove_level(self):
        """Removes the selected level."""
        selected_index = self.level_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a level to remove.", parent=self)
            return
            
        level_name = self.level_listbox.get(selected_index)
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to permanently remove the level '{level_name}'?"):
            data = self.controller.get_data()
            del data[self.current_semester]["levels"][level_name]
            self.controller.save_data(data)
            self.refresh_level_list()
            logging.info(f"Developer removed level '{level_name}' from '{self.current_semester}'")

    def go_back(self):
        """Navigates back to the SemesterScreen."""
        self.controller.show_frame("SemesterScreen")