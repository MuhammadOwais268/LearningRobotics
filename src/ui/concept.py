# File: ui/concept.py

import tkinter as tk
from tkinter import ttk, messagebox

class ConceptScreen(tk.Frame):
    """A screen that only displays the conceptual information for a level."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        self.is_dev_editing = False
        self._create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event=None):
        self.load_content()
        self.update_developer_options()

    def _create_widgets(self):
        header_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame = tk.Frame(self, bg="white")
        header_frame.pack(side='top', fill='x', padx=10, pady=5)
        main_frame.pack(side='top', fill='both', expand=True, padx=10, pady=5)

        tk.Button(header_frame, text="← Back to Levels", command=self.go_back).pack(side='left')
        self.header_label = tk.Label(header_frame, text="Concept:", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
        self.header_label.pack(side='left', padx=20)
        self.dev_edit_button = tk.Button(header_frame, text="✏️ Edit Concept", command=self.toggle_dev_edit_mode)

        h_pane = ttk.PanedWindow(main_frame, orient='horizontal')
        h_pane.pack(fill='both', expand=True)

        # Explanation Frame
        self.exp_frame = self.create_pane_section(h_pane, "Explanation", lambda: self.paste_into_widget(self.exp_text))
        self.exp_text = self.create_text_widget(self.exp_frame, wrap='word', font_family="Helvetica")
        h_pane.add(self.exp_frame, weight=2)

        # Right Pane (Code + Output)
        right_pane = tk.Frame(h_pane)
        right_pane.rowconfigure(0, weight=2)
        right_pane.rowconfigure(1, weight=1)
        right_pane.columnconfigure(0, weight=1)
        h_pane.add(right_pane, weight=3)

        self.code_frame = self.create_pane_section(right_pane, "Example Code", lambda: self.paste_into_widget(self.code_text))
        self.code_frame.grid(row=0, column=0, sticky='nsew', pady=(0,5))
        self.code_text = self.create_text_widget(self.code_frame, bg="#2b2b2b", fg="white", font_family="Courier")

        self.out_frame = self.create_pane_section(right_pane, "Expected Output", lambda: self.paste_into_widget(self.out_text))
        self.out_frame.grid(row=1, column=0, sticky='nsew')
        self.out_text = self.create_text_widget(self.out_frame, bg="#1a1a1a", fg="#4E9A06", font_family="Courier")

    def load_content(self):
        level_name = self.controller.current_level
        self.header_label.config(text=f"Concept: {level_name}")
        data = self.controller.get_data().get(self.controller.current_semester, {}).get("levels", {}).get(level_name, {}).get("concept", {})

        content_map = {self.exp_text: "explanation", self.code_text: "code", self.out_text: "output"}
        for widget, key in content_map.items():
            widget.config(state='normal')
            widget.delete(1.0, 'end')
            widget.insert('end', data.get(key, ""))
            widget.config(state='disabled')

    def go_back(self):
        self.controller.show_frame("LevelScreen")

    def toggle_dev_edit_mode(self):
        self.is_dev_editing = not self.is_dev_editing
        if self.is_dev_editing:
            self.dev_edit_button.config(text="💾 Save Concept")
            for widget in [self.exp_text, self.code_text, self.out_text]:
                widget.config(state='normal')
            self.show_paste_buttons(True)
        else:
            data = self.controller.get_data()
            concept_data = data[self.controller.current_semester]["levels"][self.controller.current_level]["concept"]
            concept_data["explanation"] = self.exp_text.get(1.0, 'end-1c')
            concept_data["code"] = self.code_text.get(1.0, 'end-1c')
            concept_data["output"] = self.out_text.get(1.0, 'end-1c')
            self.controller.save_data(data)

            self.dev_edit_button.config(text="✏️ Edit Concept")
            for widget in [self.exp_text, self.code_text, self.out_text]:
                widget.config(state='disabled')
            self.show_paste_buttons(False)
            messagebox.showinfo("Saved", "Concept content has been updated.")

    def update_developer_options(self):
        if self.controller.user_role == "developer":
            self.dev_edit_button.pack(side='right', padx=10)
            if self.is_dev_editing:
                self.show_paste_buttons(True)
        else:
            self.dev_edit_button.pack_forget()
            self.show_paste_buttons(False)

    # ✅ NEW: Adds paste button to the section header (top of text widget)
    def create_pane_section(self, parent, label_text, paste_command=None):
        frame = tk.Frame(parent, padx=5, pady=5)
        header_frame = tk.Frame(frame)
        header_frame.pack(fill='x', anchor='w')

        tk.Label(header_frame, text=label_text, font=("Helvetica", 14, "bold")).pack(side='left')

        if paste_command:
            paste_button = tk.Button(header_frame, text="📋 Paste", command=paste_command)
            paste_button.pack(side='left', padx=10)
            paste_button._is_paste_button = True  # tag it for toggling visibility
            paste_button.pack_forget()  # hide initially
            frame._paste_button = paste_button

        return frame

    def show_paste_buttons(self, show=True):
        # Scan all paste buttons and show/hide based on edit mode
        for frame in [self.exp_frame, self.code_frame, self.out_frame]:
            if hasattr(frame, '_paste_button'):
                if show:
                    frame._paste_button.pack(side='left', padx=10)
                else:
                    frame._paste_button.pack_forget()

    def paste_into_widget(self, target_widget):
        if not self.is_dev_editing:
            messagebox.showinfo("Read-Only Mode", "Please click '✏️ Edit Concept' before pasting.")
            return
        try:
            clipboard_content = self.clipboard_get()
            target_widget.insert(tk.INSERT, clipboard_content)
        except tk.TclError:
            messagebox.showwarning("Paste Error", "Clipboard is empty or contains invalid content.")

    def create_text_widget(self, parent, bg="#ffffff", fg="#000000", font_family="Helvetica", wrap='none'):
        text_widget = tk.Text(parent, wrap=wrap, state='disabled', font=(font_family, 11), relief='solid', bd=1, bg=bg, fg=fg, insertbackground=fg)
        text_widget.pack(fill='both', expand=True, pady=(5, 0))
        return text_widget
