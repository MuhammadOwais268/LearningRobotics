# File: client/src/ui/concept.py (with AI Tutor Pop-up)

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import re
import queue # Required for AI queue

class SyntaxHighlighter:
    # ... (This class is complete and correct) ...
    def __init__(self, text_widget): self.text = text_widget; self.text.bind('<KeyRelease>', self.on_key_release); self.theme = {'normal': {'foreground': '#FFFFFF', 'background': '#2b2b2b'}, 'keyword': {'foreground': '#CC7832'}, 'comment': {'foreground': '#808080'}, 'string': {'foreground': '#A5C25C'}, 'number': {'foreground': '#6897BB'}, 'preprocessor': {'foreground': '#8A653B'}}; [self.text.tag_configure(tag, **colors) for tag, colors in self.theme.items()]; self.rules = {'preprocessor': r'(#.*?)\n', 'comment': r'(\/\/.*?)\n|(/\*[\s\S]*?\*/)', 'keyword': r'\b(void|int|char|float|double|bool|const|unsigned|long|short|return|if|else|for|while|do|break|continue|struct|class|public|private|protected|new|delete|true|false|HIGH|LOW|OUTPUT|INPUT|pinMode|digitalWrite|analogWrite|delay|setup|loop|uint8_t|uint16_t|uint32_t)\b', 'string': r'(\".*?\")', 'number': r'\b([0-9]+)\b'}
    def on_key_release(self, event=None): self.highlight()
    def highlight(self, event=None):
        start_index, end_index = "1.0", "end"; [self.text.tag_remove(tag, start_index, end_index) for tag in self.theme.keys()]; self.text.tag_add('normal', start_index, end_index); text_content = self.text.get(start_index, end_index)
        for token_type, pattern in self.rules.items():
            for match in re.finditer(pattern, text_content): start, end = match.span(); match_start = f"{start_index}+{start}c"; match_end = f"{start_index}+{end}c"; self.text.tag_add(token_type, match_start, match_end)

class ConceptScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        self.is_dev_editing = False
        self._create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def _create_widgets(self):
        header_frame = tk.Frame(self, bg="#f0f0f0"); header_frame.pack(side='top', fill='x', padx=10, pady=5)
        
        # Left side of header
        left_header = tk.Frame(header_frame, bg="#f0f0f0"); left_header.pack(side='left', fill='x', expand=True)
        tk.Button(left_header, text="← Back to Levels", command=self.go_back).pack(side='left')
        tk.Button(left_header, text="🔄 Refresh", command=self.refresh_content).pack(side="left", padx=5)
        self.header_label = tk.Label(left_header, text="Concept:", font=("Helvetica", 18, "bold"), bg="#f0f0f0"); self.header_label.pack(side='left', padx=20)
        
        # Right side of header
        right_header = tk.Frame(header_frame, bg="#f0f0f0"); right_header.pack(side='right')
        self.dev_edit_button = tk.Button(right_header, text="✏️ Edit Concept", command=self.toggle_dev_edit_mode); self.dev_edit_button.pack(side='left', padx=5)
        # <<< NEW: AI Tutor Button >>>
        self.ai_button = tk.Button(right_header, text="🤖 Explain Highlighted", command=self.open_ai_tutor_popup); self.ai_button.pack(side='left')

        main_frame = tk.Frame(self, bg="white"); main_frame.pack(side='top', fill='both', expand=True, padx=10, pady=5)
        h_pane = ttk.PanedWindow(main_frame, orient='horizontal'); h_pane.pack(fill='both', expand=True)
        self.exp_frame = self.create_pane_section(h_pane, "Explanation", lambda: self.paste_into_widget(self.exp_text)); self.exp_text = self.create_text_widget(self.exp_frame, wrap='word', font_family="Helvetica"); h_pane.add(self.exp_frame, weight=2)
        right_pane = tk.Frame(h_pane); right_pane.rowconfigure(0, weight=2); right_pane.rowconfigure(1, weight=1); right_pane.columnconfigure(0, weight=1); h_pane.add(right_pane, weight=3)
        self.code_frame = self.create_pane_section(right_pane, "Example Code", lambda: self.paste_into_widget(self.code_text)); self.code_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 5))
        self.code_text = self.create_text_widget(self.code_frame, bg="#2b2b2b", fg="white", font_family="Courier")
        self.highlighter = SyntaxHighlighter(self.code_text)
        self.out_frame = self.create_pane_section(right_pane, "Expected Output", lambda: self.paste_into_widget(self.out_text)); self.out_frame.grid(row=1, column=0, sticky='nsew')
        self.out_text = self.create_text_widget(self.out_frame, bg="#1a1a1a", fg="#4E9A06", font_family="Courier")

    def on_show_frame(self, event=None):
        if self.controller.current_user and self.controller.current_semester and self.controller.current_level:
            self.controller.save_last_viewed(self.controller.current_semester, self.controller.current_level, "concept")
        self.load_content()
        self.update_developer_options()
        # Enable/disable AI button
        self.ai_button.config(state='normal' if self.controller.ai_tutor.is_available else 'disabled')

    # <<< NEW AI TUTOR METHODS (similar to library_viewer_screen) >>>
    def open_ai_tutor_popup(self):
        popup = tk.Toplevel(self); popup.title("Robo-Tutor Response"); popup.geometry("500x400")
        response_text = tk.Text(popup, wrap='word', state='disabled', font=("Helvetica", 11), padx=10, pady=10)
        response_text.pack(fill='both', expand=True)
        self.ask_ai_about_selection(response_text)
        self.process_ai_queue_for_popup(popup, response_text)

    def ask_ai_about_selection(self, response_widget):
        try:
            # Check which text box has focus to get highlighted text
            focused_widget = self.focus_get()
            if focused_widget in [self.code_text, self.exp_text, self.out_text]:
                snippet = focused_widget.get("sel.first", "sel.last")
            else: # Default to the code text if no specific focus
                snippet = self.code_text.get("sel.first", "sel.last")
        except tk.TclError:
            messagebox.showinfo("No Selection", "Please highlight some text in one of the boxes to explain.")
            response_widget.master.destroy(); return

        full_code = self.code_text.get("1.0", "end-1c")
        question = "What does this highlighted text mean in the context of this lesson?"

        response_widget.config(state='normal'); response_widget.delete(1.0, 'end'); response_widget.insert(1.0, ">>> Robo-Tutor is thinking...")
        response_widget.config(state='disabled')

        self.controller.ai_tutor.get_ai_explanation(
            question=question, code_snippet=snippet, full_code_context=full_code
        )

    def process_ai_queue_for_popup(self, popup, response_widget):
        try:
            response = self.controller.ai_tutor.response_queue.get_nowait()
            response_widget.config(state='normal'); response_widget.delete(1.0, 'end'); response_widget.insert(1.0, response)
            response_widget.config(state='disabled')
        except queue.Empty:
            if popup.winfo_exists():
                self.after(200, lambda: self.process_ai_queue_for_popup(popup, response_widget))

    # ... (All other methods are unchanged and correct) ...
    def refresh_content(self):
        if self.is_dev_editing: messagebox.showwarning("Refresh Blocked", "Please save or cancel your changes before refreshing."); return
        self.load_content(); messagebox.showinfo("Refreshed", "Concept content has been updated.")
    def load_content(self):
        if not self.controller.current_semester or not self.controller.current_level: return
        level_name = self.controller.current_level; self.header_label.config(text=f"Concept: {level_name}"); data = self.controller.get_data()
        concept_data = data.get(self.controller.current_semester, {}).get("levels", {}).get(level_name, {}).get("concept", {})
        content_map = {self.exp_text: "explanation", self.code_text: "code", self.out_text: "output"}
        for widget, key in content_map.items():
            widget.config(state='normal'); widget.delete(1.0, 'end'); widget.insert('end', concept_data.get(key, ""))
            if not self.is_dev_editing: widget.config(state='disabled')
        self.highlighter.highlight()
    def paste_into_widget(self, target_widget):
        if not self.is_dev_editing: return
        try:
            clipboard_content = self.clipboard_get(); target_widget.delete(1.0, 'end'); target_widget.insert('end', clipboard_content)
            if target_widget == self.code_text: self.highlighter.highlight()
        except tk.TclError: messagebox.showwarning("Paste Error", "Clipboard is empty.")
    def toggle_dev_edit_mode(self):
        self.is_dev_editing = not self.is_dev_editing
        if self.is_dev_editing:
            self.dev_edit_button.config(text="💾 Save Concept"); [w.config(state='normal') for w in [self.exp_text, self.code_text, self.out_text]]; self.show_paste_buttons(True)
        else:
            data = self.controller.get_data()
            level_data = data.setdefault(self.controller.current_semester, {}).setdefault("levels", {}).setdefault(self.controller.current_level, {})
            concept_data = level_data.setdefault("concept", {}); concept_data["explanation"] = self.exp_text.get(1.0, 'end-1c'); concept_data["code"] = self.code_text.get(1.0, 'end-1c'); concept_data["output"] = self.out_text.get(1.0, 'end-1c')
            self.controller.save_data(data); messagebox.showinfo("Saved", "Concept content has been updated.")
            self.dev_edit_button.config(text="✏️ Edit Concept"); [w.config(state='disabled') for w in [self.exp_text, self.code_text, self.out_text]]; self.show_paste_buttons(False)
    def update_developer_options(self):
        is_dev = self.controller.current_user and self.controller.current_user.get('role') == "developer"
        if is_dev: self.dev_edit_button.pack(side='left', padx=5); self.show_paste_buttons(self.is_dev_editing)
        else: self.is_dev_editing = False; self.dev_edit_button.pack_forget(); self.show_paste_buttons(False)
    def go_back(self): self.is_dev_editing = False; self.update_developer_options(); self.controller.show_frame("LevelScreen")
    def create_pane_section(self, parent, label_text, paste_command=None):
        frame = tk.Frame(parent, padx=5, pady=5); header_frame = tk.Frame(frame); header_frame.pack(fill='x', anchor='w')
        tk.Label(header_frame, text=label_text, font=("Helvetica", 14, "bold")).pack(side='left')
        if paste_command: paste_button = tk.Button(header_frame, text="📋", command=paste_command); paste_button._is_paste_button = True; frame._paste_button = paste_button
        return frame
    def show_paste_buttons(self, show=True):
        for frame in [self.exp_frame, self.code_frame, self.out_frame]:
            if hasattr(frame, '_paste_button'):
                if show: frame._paste_button.pack(side='left', padx=10)
                else: frame._paste_button.pack_forget()
    def create_text_widget(self, parent, bg="#ffffff", fg="#000000", font_family="Helvetica", wrap='none'):
        text_widget = tk.Text(parent, wrap=wrap, state='disabled', font=(font_family, 11), relief='solid', bd=1, bg=bg, fg=fg, insertbackground=fg)
        text_widget.pack(fill='both', expand=True, pady=(5, 0))
        return text_widget