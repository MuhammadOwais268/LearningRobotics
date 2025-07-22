# File: client/src/ui/library_viewer_screen.py (Updated for Direct Edit Model)

import tkinter as tk
from tkinter import ttk, messagebox
import os
import re

class SyntaxHighlighter:
    # ... (This class is complete and correct) ...
    def __init__(self, text_widget): self.text = text_widget; self.theme = {'normal': {'foreground': '#FFFFFF', 'background': '#2b2b2b'}, 'keyword': {'foreground': '#CC7832'}, 'comment': {'foreground': '#808080'}, 'string': {'foreground': '#A5C25C'}, 'number': {'foreground': '#6897BB'}, 'preprocessor': {'foreground': '#8A653B'}}; [self.text.tag_configure(tag, **colors) for tag, colors in self.theme.items()]; self.rules = {'preprocessor': r'(#.*?)\n', 'comment': r'(\/\/.*?)\n|(/\*[\s\S]*?\*/)', 'keyword': r'\b(void|int|char|float|double|bool|const|unsigned|long|short|return|if|else|for|while|do|break|continue|struct|class|public|private|protected|new|delete|true|false|HIGH|LOW|OUTPUT|INPUT|pinMode|digitalWrite|analogWrite|delay|setup|loop|uint8_t|uint16_t|uint32_t)\b', 'string': r'(\".*?\")', 'number': r'\b([0-9]+)\b'}
    def highlight(self):
        start_index, end_index = "1.0", "end"; [self.text.tag_remove(tag, start_index, end_index) for tag in self.theme.keys()]; self.text.tag_add('normal', start_index, end_index); text_content = self.text.get(start_index, end_index)
        for token_type, pattern in self.rules.items():
            for match in re.finditer(pattern, text_content): start, end = match.span(); match_start = f"{start_index}+{start}c"; match_end = f"{start_index}+{end}c"; self.text.tag_add(token_type, match_start, match_end)

class LibraryViewerScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0e0e0")
        self.controller = controller
        self.current_file_rel_path = None
        self._create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def _create_widgets(self):
        header = tk.Frame(self, bg="#e0e0e0"); header.pack(side='top', fill='x', padx=5, pady=5)
        tk.Button(header, text="← Back to Implementation", command=self.go_back).pack(side='left')
        self.title_label = tk.Label(header, text="Viewing Library File:", font=("Helvetica", 18, "bold"), bg="#e0e0e0"); self.title_label.pack(side='left', padx=20)
        main_pane = ttk.PanedWindow(self, orient='horizontal'); main_pane.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        code_frame = tk.Frame(main_pane)
        tk.Label(code_frame, text="Source Code (Read-Only)", font=("Helvetica", 12, "bold")).pack(anchor='w', padx=5, pady=2)
        self.code_viewer = tk.Text(code_frame, wrap='none', state='disabled', font=("Courier", 11), bg="#2b2b2b", fg="white")
        self.code_viewer.pack(fill='both', expand=True)
        self.highlighter = SyntaxHighlighter(self.code_viewer)
        main_pane.add(code_frame, weight=2)
        exp_frame = tk.Frame(main_pane)
        tk.Label(exp_frame, text="Explanation", font=("Helvetica", 12, "bold")).pack(anchor='w', padx=5, pady=2)
        self.explanation_text = tk.Text(exp_frame, wrap='word', state='disabled', font=("Helvetica", 11))
        self.explanation_text.pack(fill='both', expand=True)
        main_pane.add(exp_frame, weight=1)

    def on_show_frame(self, event=None):
        self.current_file_rel_path = self.controller.library_file_to_view
        if not self.current_file_rel_path:
            messagebox.showerror("Error", "No library file was selected."); self.go_back(); return
        self.title_label.config(text=f"Viewing: {os.path.basename(self.current_file_rel_path)}")
        self.load_file_content()

    def load_file_content(self):
        """Reads the source and explanation files from the permanent 'Robotics' folder."""
        base_path = self.controller.get_robotics_project_path()
        source_file_path = os.path.join(base_path, self.current_file_rel_path)
        explanation_file_path = source_file_path + ".txt"

        try:
            with open(source_file_path, 'r') as f: source_content = f.read()
            self.code_viewer.config(state='normal'); self.code_viewer.delete(1.0, 'end'); self.code_viewer.insert(1.0, source_content)
            self.highlighter.highlight(); self.code_viewer.config(state='disabled')
        except FileNotFoundError:
            self.code_viewer.config(state='normal'); self.code_viewer.delete(1.0, 'end'); self.code_viewer.insert(1.0, f"Error: Source file not found at\n{source_file_path}"); self.code_viewer.config(state='disabled')
            
        try:
            with open(explanation_file_path, 'r') as f: explanation_content = f.read()
            self.explanation_text.config(state='normal'); self.explanation_text.delete(1.0, 'end'); self.explanation_text.insert(1.0, explanation_content); self.explanation_text.config(state='disabled')
        except FileNotFoundError:
            self.explanation_text.config(state='normal'); self.explanation_text.delete(1.0, 'end'); self.explanation_text.insert(1.0, "No explanation file found for this item."); self.explanation_text.config(state='disabled')

    def go_back(self):
        self.controller.show_frame("ImplementationScreen")