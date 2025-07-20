import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

class SemesterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        self.selected_semester = None
        self.DEFAULT_BG = "#ffffff"
        self.SELECTED_BG = "#aed6f1"

        header_frame = tk.Frame(self, bg="#f4f6f7")
        header_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        tk.Button(header_frame, text="← Back to Mode Selection", command=self.go_back).pack(side="left")
        tk.Button(header_frame, text="Refresh", command=self.refresh_data, font=("Helvetica", 10), bg="#3498db", fg="white").pack(side="left", padx=5)

        self.student_count_label = tk.Label(header_frame, text="Visible Students: 0", font=("Helvetica", 10), bg="#f4f6f7")
        self.student_count_label.pack(side="right", padx=10)
        
        main_content_frame = tk.Frame(self, bg="#f4f6f7")
        main_content_frame.pack(side="top", fill="both", expand=True)
        self.title_label = tk.Label(main_content_frame, text="Select a Semester", font=("Helvetica", 32, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self.title_label.pack(pady=(20, 10))
        self.instruction_label = tk.Label(main_content_frame, font=("Helvetica", 11), bg="#f4f6f7", fg="#34495e")
        self.instruction_label.pack(pady=(0, 20))
        self.button_grid_frame = tk.Frame(main_content_frame, bg="#f4f6f7")
        self.button_grid_frame.pack(pady=20, padx=20)
        self.continue_button = tk.Button(main_content_frame, text="Continue to Level Selection", font=("Helvetica", 14, "bold"), fg="white", bg="#27ae60", command=self.on_continue_click)
        
        self.dev_tools_frame = tk.Frame(self, bg="#e0e0e0", bd=2, relief=tk.GROOVE)
        self.setup_developer_tools()

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def refresh_data(self):
        """Manually refresh semester data and UI."""
        self.controller.get_data()
        self.refresh_semester_buttons()
        self.update_dev_tool_states()

    def on_show_frame(self, event):
        """REWRITTEN: Correct logic for all roles and modes."""
        self.selected_semester = None
        
        # Load the correct data (online or offline)
        self.controller.get_data()
        self.refresh_semester_buttons()
        
        is_dev = self.controller.current_user.get('role') == "developer"
        is_online = self.controller.is_online

        # --- Configure UI based on status ---

        # 1. Configure Title and Online-only elements
        if is_online:
            self.title_label.config(text=f"Class: {self.controller.current_class_code}")
            # Only show student count if online and a developer
            if is_dev:
                self.student_count_label.pack(side="right", padx=10)
            else:
                self.student_count_label.pack_forget()
        else: # Offline
            self.title_label.config(text="Offline Semesters")
            self.student_count_label.pack_forget()

        # 2. Configure Developer vs. Student UI
        if is_dev:
            # Developer sees admin tools in BOTH online and offline modes
            self.instruction_label.config(text="Select a semester to edit, remove, or continue.")
            self.continue_button.pack(pady=(10, 20))
            self.dev_tools_frame.pack(side="bottom", fill="x", padx=10, pady=10)
            self.update_dev_tool_states()
        else: # Student
            self.instruction_label.config(text="Click a semester to see its levels.")
            self.continue_button.pack_forget()
            self.dev_tools_frame.pack_forget()

    def go_back(self):
        self.controller.network_client.stop_live_feed()
        self.controller.show_frame("ModeSelectionScreen")

    def refresh_semester_buttons(self):
        for widget in self.button_grid_frame.winfo_children(): widget.destroy()
        semesters = self.controller.app_data.keys()
        is_dev = self.controller.current_user.get('role') == "developer"
        
        for i, semester_name in enumerate(semesters):
            bg_color = self.SELECTED_BG if semester_name == self.selected_semester else self.DEFAULT_BG
            button = tk.Button(self.button_grid_frame, text=semester_name, font=("Helvetica", 16), width=15, pady=20, bg=bg_color)
            if is_dev:
                button.config(command=lambda s=semester_name: self.on_semester_select(s))
            else:
                button.config(command=lambda s=semester_name: self.navigate_to_semester(s))
            row, col = divmod(i, 3)
            button.grid(row=row, column=col, padx=15, pady=15)

    def update_student_count(self, count):
        self.student_count_label.config(text=f"Visible Students: {count}")

    def on_semester_select(self, semester_name):
        self.selected_semester = semester_name if self.selected_semester != semester_name else None
        self.refresh_semester_buttons()
        self.update_dev_tool_states()

    def on_continue_click(self):
        if self.selected_semester: self.navigate_to_semester(self.selected_semester)

    def navigate_to_semester(self, semester_name):
        self.controller.current_semester = semester_name
        self.controller.show_frame("LevelScreen")

    def setup_developer_tools(self):
        tk.Label(self.dev_tools_frame, text="Semester Developer Tools", font=("Helvetica", 14, "bold"), bg="#e0e0e0").pack()
        bar = tk.Frame(self.dev_tools_frame, bg="#e0e0e0")
        bar.pack(pady=10, fill='x', padx=10)
        tk.Button(bar, text="Add New Semester", command=self.add_semester).pack(side="left", expand=True, fill='x', padx=5)
        self.edit_button = tk.Button(bar, text="Edit Selected Name", command=self.edit_semester)
        self.edit_button.pack(side="left", expand=True, fill='x', padx=5)
        self.remove_button = tk.Button(bar, text="Remove Selected", command=self.remove_semester, bg="#c0392b", fg="white")
        self.remove_button.pack(side="left", expand=True, fill='x', padx=5)

    def update_dev_tool_states(self):
        state = "normal" if self.selected_semester else "disabled"
        self.continue_button.config(state=state)
        self.edit_button.config(state=state)
        self.remove_button.config(state=state)

    def add_semester(self):
        new_name = simpledialog.askstring("Add Semester", "Enter name for the new semester:")
        if not new_name or not new_name.strip(): return
        data = self.controller.get_data()
        if new_name in data:
            messagebox.showerror("Error", "A semester with this name already exists.")
            return
        data[new_name] = {"levels": {}}
        self.controller.save_data(data)
        self.refresh_semester_buttons()

    def edit_semester(self):
        if not self.selected_semester: return
        new_name = simpledialog.askstring("Rename Semester", "Enter new name:", initialvalue=self.selected_semester)
        if not new_name or not new_name.strip() or new_name == self.selected_semester: return
        data = self.controller.get_data()
        if new_name in data:
            messagebox.showerror("Error", "A semester with this name already exists.")
            return
        data[new_name] = data.pop(self.selected_semester)
        self.selected_semester = new_name
        self.controller.save_data(data)
        self.refresh_semester_buttons()

    def remove_semester(self):
        if not self.selected_semester: return
        if messagebox.askyesno("Confirm", f"Delete '{self.selected_semester}'?"):
            data = self.controller.get_data()
            del data[self.selected_semester]
            self.selected_semester = None
            self.controller.save_data(data)
            self.refresh_semester_buttons()
            self.update_dev_tool_states()