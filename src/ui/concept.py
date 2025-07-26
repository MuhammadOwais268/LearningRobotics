# File: client/src/ui/concept.py (Final Version with Embedded AI Tutor)

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import re
import queue

class SyntaxHighlighter:
    def __init__(self, text_widget): self.text = text_widget; self.theme = {'normal': {'foreground': '#FFFFFF', 'background': '#2b2b2b'}, 'keyword': {'foreground': '#CC7832'}, 'comment': {'foreground': '#808080'}, 'string': {'foreground': '#A5C25C'}, 'number': {'foreground': '#6897BB'}, 'preprocessor': {'foreground': '#8A653B'}}; [self.text.tag_configure(tag, **colors) for tag, colors in self.theme.items()]; self.rules = {'preprocessor': r'(#.*?)\n', 'comment': r'(\/\/.*?)\n|(/\*[\s\S]*?\*/)', 'keyword': r'\b(void|int|char|float|double|bool|const|unsigned|long|short|return|if|else|for|while|do|break|continue|struct|class|public|private|protected|new|delete|true|false|HIGH|LOW|OUTPUT|INPUT|pinMode|digitalWrite|analogWrite|delay|setup|loop|uint8_t|uint16_t|uint32_t)\b', 'string': r'(\".*?\")', 'number': r'\b([0-9]+)\b'}
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

    # In client/src/ui/concept.py

    def _create_widgets(self):
        # --- Header ---
        header_frame = tk.Frame(self, bg="#f0f0f0"); header_frame.pack(side='top', fill='x', padx=10, pady=5)
        left_header_frame = tk.Frame(header_frame, bg="#f0f0f0"); left_header_frame.pack(side='left', fill='x', expand=True)
        tk.Button(left_header_frame, text="← Back to Levels", command=self.go_back).pack(side='left')
        tk.Button(left_header_frame, text="🔄 Refresh", command=self.refresh_content).pack(side="left", padx=5)
        self.header_label = tk.Label(left_header_frame, text="Concept:", font=("Helvetica", 18, "bold"), bg="#f0f0f0"); self.header_label.pack(side='left', padx=20)
        right_header_frame = tk.Frame(header_frame, bg="#f0f0f0"); right_header_frame.pack(side='right')
        self.dev_edit_button = tk.Button(right_header_frame, text="✏️ Edit Concept", command=self.toggle_dev_edit_mode)
        
        # --- Main Content Panes ---
        main_v_pane = ttk.PanedWindow(self, orient='vertical'); main_v_pane.pack(fill='both', expand=True, padx=10, pady=5)
        top_frame = tk.Frame(main_v_pane); main_v_pane.add(top_frame, weight=3)
        bottom_frame = tk.Frame(main_v_pane, bg="#f0f0f0"); main_v_pane.add(bottom_frame, weight=1)

        h_pane = ttk.PanedWindow(top_frame, orient='horizontal'); h_pane.pack(fill='both', expand=True)
        self.exp_frame = self.create_pane_section(h_pane, "Explanation", lambda: self.paste_into_widget(self.exp_text)); self.exp_text = self.create_text_widget(self.exp_frame, wrap='word'); h_pane.add(self.exp_frame, weight=2)
        right_pane = tk.Frame(h_pane); right_pane.rowconfigure(0, weight=2); right_pane.rowconfigure(1, weight=1); right_pane.columnconfigure(0, weight=1); h_pane.add(right_pane, weight=3)
        self.code_frame = self.create_pane_section(right_pane, "Example Code", lambda: self.paste_into_widget(self.code_text)); self.code_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 5))
        self.code_text = self.create_text_widget(self.code_frame, bg="#2b2b2b", fg="white", font_family="Courier"); self.highlighter = SyntaxHighlighter(self.code_text)
        self.out_frame = self.create_pane_section(right_pane, "Expected Output", lambda: self.paste_into_widget(self.out_text)); self.out_frame.grid(row=1, column=0, sticky='nsew')
        self.out_text = self.create_text_widget(self.out_frame, bg="#1a1a1a", fg="#4E9A06", font_family="Courier")
        
        # <<< MODIFIED AI TUTOR PANE LAYOUT >>>
        ai_frame = tk.Frame(bottom_frame, padx=5, pady=5, bg="#f0f0f0")
        ai_frame.pack(fill='both', expand=True)
        tk.Label(ai_frame, text="🤖 Robo-Tutor", font=("Helvetica", 12, "bold"), bg="#f0f0f0").pack(anchor='w')

        # Frame for the input controls, now at the top
        ai_input_frame = tk.Frame(ai_frame, bg="#f0f0f0"); ai_input_frame.pack(fill='x', pady=(5,2))
        
        self.ai_question_entry = tk.Entry(ai_input_frame, font=("Helvetica", 11), relief='solid', bd=1)
        self.ai_question_entry.pack(side='left', fill='x', expand=True, ipady=4)
        self.ai_question_entry.bind("<Return>", self.on_ask_button_click)
        
        tk.Button(ai_input_frame, text="Ask", command=self.on_ask_button_click).pack(side='left', padx=(5,0))
        tk.Button(ai_input_frame, text="Explain Highlighted", command=self.on_explain_highlighted_click).pack(side='left', padx=5)

        # Frame for the response text area, now below
        ai_response_frame = tk.Frame(ai_frame)
        ai_response_frame.pack(fill='both', expand=True)
        self.ai_response_text = tk.Text(ai_response_frame, wrap='word', state='disabled', font=("Helvetica", 11), relief='solid', bd=1)
        self.ai_response_text.pack(fill='both', expand=True)

    def on_show_frame(self, event=None):
        if self.controller.current_user and self.controller.current_semester and self.controller.current_level:
            self.controller.save_last_viewed(self.controller.current_semester, self.controller.current_level, "concept")
        self.load_content(); self.update_developer_options(); self.after(100, self.process_ai_queue)
        self.ai_response_text.config(state='normal'); self.ai_response_text.delete(1.0, 'end')
        initial_message = "Hello! Highlight text in any of the boxes above and click 'Explain Highlighted', or type a general question below."
        if not self.controller.ai_tutor.is_available: initial_message = "AI Tutor is offline."
        self.ai_response_text.insert(1.0, initial_message); self.ai_response_text.config(state='disabled')
        
    def on_ask_button_click(self, event=None):
        question = self.ai_question_entry.get()
        if not question.strip(): return
        full_code = self.code_text.get("1.0", "end-1c")
        self.ai_response_text.config(state='normal'); self.ai_response_text.delete(1.0, 'end'); self.ai_response_text.insert(1.0, ">>> Robo-Tutor is thinking...")
        self.ai_response_text.config(state='disabled'); self.controller.ai_tutor.get_ai_explanation(question=question, full_code_context=full_code)

    def on_explain_highlighted_click(self):
        snippet = ""
        for widget in [self.exp_text, self.code_text, self.out_text]:
            try:
                snippet = widget.get("sel.first", "sel.last")
                if snippet: break
            except tk.TclError: continue
        if not snippet: messagebox.showinfo("No Selection", "Please highlight text in a box to explain."); return
        full_code = self.code_text.get("1.0", "end-1c"); question = "What does this highlighted text mean?"
        self.ai_response_text.config(state='normal'); self.ai_response_text.delete(1.0, 'end'); self.ai_response_text.insert(1.0, ">>> Robo-Tutor is thinking...")
        self.ai_response_text.config(state='disabled'); self.controller.ai_tutor.get_ai_explanation(question=question, code_snippet=snippet, full_code_context=full_code)

    def process_ai_queue(self):
        try:
            response = self.controller.ai_tutor.response_queue.get_nowait()
            self.ai_response_text.config(state='normal'); self.ai_response_text.delete(1.0, 'end'); self.ai_response_text.insert(1.0, response)
            self.ai_response_text.config(state='disabled'); self.ai_question_entry.delete(0, 'end')
        except queue.Empty: pass
        finally: self.after(200, self.process_ai_queue)
    
    def create_text_widget(self, parent, bg="#ffffff", fg="#000000", font_family="Helvetica", wrap='none'):
        text_widget = tk.Text(parent, wrap=wrap, state='disabled', font=(font_family, 11), relief='solid', bd=1, bg=bg, fg=fg, insertbackground="black" if bg=="#ffffff" else "white", selectbackground="#0078D4", selectforeground="white")
        text_widget.pack(fill='both', expand=True, pady=(5, 0))
        return text_widget
    def refresh_content(self):
        if self.is_dev_editing: messagebox.showwarning("Refresh Blocked", "Please save or cancel changes before refreshing."); return
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
        self.dev_edit_button.pack_forget()
        if is_dev:
            self.dev_edit_button.pack(in_=self.dev_edit_button.master, side='right', padx=10)
            self.show_paste_buttons(self.is_dev_editing)
        else:
            self.is_dev_editing = False; self.show_paste_buttons(False)
    def go_back(self): self.is_dev_editing = False; self.update_developer_options(); self.controller.show_frame("LevelScreen")
    def create_pane_section(self, parent, label_text, paste_command=None):
        frame = tk.Frame(parent, padx=5, pady=5); header_frame = tk.Frame(frame); header_frame.pack(fill='x', anchor='w')
        tk.Label(header_frame, text=label_text, font=("Helvetica", 14, "bold")).pack(side='left')
        if paste_command:
            paste_button = tk.Button(header_frame, text="📋", command=paste_command); paste_button._is_paste_button = True; frame._paste_button = paste_button
        return frame
    def show_paste_buttons(self, show=True):
        for frame in [self.exp_frame, self.code_frame, self.out_frame]:
            if hasattr(frame, '_paste_button'):
                if show: frame._paste_button.pack(side='left', padx=10)
                else: frame._paste_button.pack_forget()