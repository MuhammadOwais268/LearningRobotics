# File: client/src/ui/library_viewer_screen.py (Final Version with AI Tutor)

import tkinter as tk
from tkinter import ttk, messagebox
import os
import re
import queue # Required for the AI response queue

class SyntaxHighlighter:
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
        tk.Button(header, text="← Back to Project", command=self.go_back).pack(side='left')
        self.title_label = tk.Label(header, text="File Viewer", font=("Helvetica", 18, "bold"), bg="#e0e0e0"); self.title_label.pack(side='left', padx=20)
        
        # <<< NEW: AI Tutor Button in the Header >>>
        self.ai_button = tk.Button(header, text="🤖 Explain Highlighted", command=self.open_ai_tutor_popup)
        self.ai_button.pack(side='right', padx=10)
        
        main_pane = ttk.PanedWindow(self, orient='horizontal'); main_pane.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        code_frame = tk.Frame(main_pane)
        self.code_label = tk.Label(code_frame, text="Source Code", font=("Helvetica", 12, "bold")); self.code_label.pack(anchor='w', padx=5, pady=2)
        self.code_viewer = tk.Text(code_frame, wrap='none', state='disabled', font=("Courier", 11), bg="#2b2b2b", fg="white", insertbackground="white")
        self.code_viewer.pack(fill='both', expand=True)
        self.highlighter = SyntaxHighlighter(self.code_viewer)
        main_pane.add(code_frame, weight=2)
        exp_frame = tk.Frame(main_pane)
        tk.Label(exp_frame, text="Explanation", font=("Helvetica", 12, "bold")).pack(anchor='w', padx=5, pady=2)
        self.explanation_text = tk.Text(exp_frame, wrap='word', state='disabled', font=("Helvetica", 11), padx=5, pady=5)
        self.explanation_text.pack(fill='both', expand=True)
        self.explanation_text.tag_configure("h1", font=("Helvetica", 16, "bold"), foreground="#2c3e50", spacing3=10); self.explanation_text.tag_configure("h2", font=("Helvetica", 12, "bold"), spacing3=8); self.explanation_text.tag_configure("bold", font=("Helvetica", 10, "bold")); self.explanation_text.tag_configure("code", font=("Courier", 10), background="#f0f0f0", relief='solid', borderwidth=1); self.explanation_text.tag_configure("bullet", lmargin1=25, lmargin2=25)
        main_pane.add(exp_frame, weight=1)

    def on_show_frame(self, event=None):
        self.current_file_rel_path = self.controller.library_file_to_view
        if not self.current_file_rel_path: messagebox.showerror("Error", "No file was selected."); self.go_back(); return
        is_main_cpp = self.current_file_rel_path == 'src/main.cpp'
        self.title_label.config(text="Editing: main.cpp" if is_main_cpp else f"Viewing: {os.path.basename(self.current_file_rel_path)}")
        self.code_label.config(text="Code Editor" if is_main_cpp else "Source Code (Read-Only)")
        self.code_viewer.config(state='normal' if is_main_cpp else 'disabled')
        if is_main_cpp: self.highlighter.text.bind('<KeyRelease>', self.highlighter.highlight)
        else: self.highlighter.text.unbind('<KeyRelease>')
        # Enable/disable AI button
        self.ai_button.config(state='normal' if self.controller.ai_tutor.is_available else 'disabled')
        self.load_file_content()

    def load_file_content(self):
        # ... (This method is unchanged and correct) ...
        base_path = self.controller.get_robotics_project_path(); source_file_path = os.path.join(base_path, self.current_file_rel_path); explanation_file_path = source_file_path + ".txt"
        is_editable = self.code_viewer.cget('state') == 'normal'
        try:
            with open(source_file_path, 'r') as f: source_content = f.read()
            if not is_editable: self.code_viewer.config(state='normal')
            self.code_viewer.delete(1.0, 'end'); self.code_viewer.insert(1.0, source_content)
            self.highlighter.highlight()
            if not is_editable: self.code_viewer.config(state='disabled')
        except FileNotFoundError: pass
        self.explanation_text.config(state='normal'); self.explanation_text.delete(1.0, 'end')
        try:
            with open(explanation_file_path, 'r') as f: explanation_content = f.read()
            self.parse_and_display_explanation(explanation_content)
        except FileNotFoundError: self.explanation_text.insert(1.0, "No explanation file found for this item.")
        self.explanation_text.config(state='disabled')

    # =================================================================
    # <<< NEW AI TUTOR METHODS FOR THIS SCREEN >>>
    # =================================================================
    def open_ai_tutor_popup(self):
        """Creates a new pop-up window for the AI tutor response."""
        popup = tk.Toplevel(self)
        popup.title("Robo-Tutor Response")
        popup.geometry("500x400")
        
        response_text = tk.Text(popup, wrap='word', state='disabled', font=("Helvetica", 11), padx=10, pady=10)
        response_text.pack(fill='both', expand=True)
        
        # Start the process of asking the AI and populating this text box
        self.ask_ai_about_selection(response_text)
        
        # Start the queue checker for this specific pop-up
        self.process_ai_queue_for_popup(popup, response_text)

    def ask_ai_about_selection(self, response_widget):
        """Gets the highlighted text and sends the request to the AI Tutor."""
        try:
            snippet = self.code_viewer.get("sel.first", "sel.last")
        except tk.TclError:
            messagebox.showinfo("No Selection", "Please highlight a piece of code to explain.")
            response_widget.master.destroy() # Close the pop-up
            return

        full_code = self.code_viewer.get("1.0", "end-1c")
        question = "What does this highlighted library code do and why is it important?"

        # Show "Thinking..." message in the pop-up
        response_widget.config(state='normal')
        response_widget.delete(1.0, 'end')
        response_widget.insert(1.0, ">>> Robo-Tutor is thinking...")
        response_widget.config(state='disabled')

        # Call the controller's AI tutor in a background thread
        self.controller.ai_tutor.get_ai_explanation(
            question=question, 
            code_snippet=snippet, 
            full_code_context=full_code
        )

    def process_ai_queue_for_popup(self, popup, response_widget):
        """Periodically checks the AI response queue for the pop-up."""
        try:
            response = self.controller.ai_tutor.response_queue.get_nowait()
            response_widget.config(state='normal')
            response_widget.delete(1.0, 'end')
            response_widget.insert(1.0, response)
            response_widget.config(state='disabled')
        except queue.Empty:
            # If the popup is still open, check again
            if popup.winfo_exists():
                self.after(200, lambda: self.process_ai_queue_for_popup(popup, response_widget))

    # --- Other methods are unchanged and correct ---
    def parse_and_display_explanation(self, content):
        for line in content.splitlines():
            if line.startswith('[h1]'): self.explanation_text.insert('end', line.replace('[h1]', '').replace('[/h1]', '') + '\n\n', 'h1')
            elif line.startswith('[h2]'): self.explanation_text.insert('end', line.replace('[h2]', '').replace('[/h2]', '') + '\n', 'h2')
            elif line.strip().startswith('*'): self.explanation_text.insert('end', f"  • {line.strip()[1:].strip()}\n", 'bullet')
            elif line.strip() == '---': self.explanation_text.insert('end', ' \n', 'h2'); self.explanation_text.insert('end', '—' * 50 + '\n', ('h2', 'center')); self.explanation_text.insert('end', ' \n', 'h2')
            else: self.parse_and_insert_inline(line + '\n')
    def parse_and_insert_inline(self, line):
        pattern = r'(\[(b|c)\](.*?)\[\/\2\])'; last_end = 0
        for match in re.finditer(pattern, line):
            start, end = match.span(); tag_type, content = match.group(2), match.group(3)
            self.explanation_text.insert('end', line[last_end:start])
            tag_map = {'b': 'bold', 'c': 'code'}; self.explanation_text.insert('end', content, tag_map.get(tag_type)); last_end = end
        self.explanation_text.insert('end', line[last_end:])
    def go_back(self):
        if self.current_file_rel_path == 'src/main.cpp':
            if messagebox.askyesno("Save?", "Do you want to save your changes to main.cpp?"):
                base_path = self.controller.get_robotics_project_path(); file_path = os.path.join(base_path, self.current_file_rel_path)
                try:
                    with open(file_path, 'w') as f: f.write(self.code_viewer.get(1.0, 'end-1c'))
                except Exception as e: messagebox.showerror("Save Error", f"Could not save file: {e}")
        self.controller.show_frame("ImplementationScreen")