import tkinter as tk
from tkinter import scrolledtext, PanedWindow, messagebox
import logging

try:
    from pygments import lex
    from pygments.lexers import CppLexer
    from pygments.styles import get_style_by_name
except ImportError:
    logging.critical("Pygments library not found! Run 'pip install pygments' for syntax highlighting.")
    lex = None

# --- Reusable Component for a Labeled Text Box ---
class LabeledText(tk.Frame):
    def __init__(self, parent, title, text_font, is_code=False):
        super().__init__(parent, bg="white", bd=1, relief="solid")
        tk.Label(self, text=f" {title} ", font=("Helvetica", 12, "bold"), bg="white").pack(anchor="nw")
        
        if is_code and lex:
            self.text_widget = CodeViewer(self, font=text_font)
        else:
            self.text_widget = scrolledtext.ScrolledText(self, font=text_font, wrap=tk.WORD, bd=0, relief="flat", padx=5, pady=5)
        
        self.text_widget.pack(fill="both", expand=True)

    def get(self):
        return self.text_widget.get("1.0", "end-1c")

    def set(self, content):
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)

    def set_state(self, state):
        self.text_widget.config(state=state)

# --- Custom Code Viewer with Syntax Highlighting ---
class CodeViewer(scrolledtext.ScrolledText):
    def __init__(self, parent, font, style="monokai", *args, **kwargs):
        super().__init__(parent, font=font, wrap=tk.WORD, bd=0, relief="flat", padx=5, pady=5, *args, **kwargs)
        self._highlight_timer = None
        self.lexer = CppLexer()
        self.style = get_style_by_name(style)
        self._configure_tags()
        self.bind("<KeyRelease>", self._schedule_highlight)

    def _configure_tags(self):
        for token, style_info in self.style:
            kwargs = {}
            if style_info['color']: kwargs['foreground'] = f"#{style_info['color']}"
            if style_info['bold']: kwargs['font'] = ("Courier New", 11, "bold")
            if style_info['italic']: kwargs['font'] = ("Courier New", 11, "italic")
            self.tag_configure(str(token), **kwargs)

    def _schedule_highlight(self, event=None):
        if self._highlight_timer: self.after_cancel(self._highlight_timer)
        self._highlight_timer = self.after(100, self._highlight_syntax)

    def _highlight_syntax(self, event=None):
        for tag in self.tag_names():
            if str(tag).startswith("Token"): self.tag_remove(tag, "1.0", "end")
        text_content = self.get("1.0", "end-1c")
        start_index = "1.0"
        for token, content in lex(text_content, self.lexer):
            end_index = f"{start_index}+{len(content)}c"
            self.tag_add(str(token), start_index, end_index)
            start_index = end_index

# --- The Main Screen ---
class ConceptScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        self._current_content = {}

        # --- Header ---
        header_frame = tk.Frame(self, bg="#f4f6f7")
        header_frame.pack(pady=10, padx=20, fill="x")
        tk.Button(header_frame, text="← Back to Levels", command=self.go_back).pack(side="left")
        self.title_label = tk.Label(header_frame, text="", font=("Helvetica", 24, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self.title_label.pack(side="left", expand=True)
        self.save_button = tk.Button(header_frame, text="✓ Save Changes", command=self.save_content, bg="#27ae60", fg="white")

        # --- Paned Window Layout ---
        main_pane = PanedWindow(self, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg="#f4f6f7", sashwidth=8)
        main_pane.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        top_pane = PanedWindow(main_pane, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=8)
        main_pane.add(top_pane, stretch="always", minsize=200)

        # --- Create and Add Widgets using the LabeledText Component ---
        self.code_viewer = LabeledText(top_pane, "Code Viewer", ("Courier New", 11), is_code=True)
        self.explanation_text = LabeledText(top_pane, "Code Explanation", ("Helvetica", 11))
        self.output_text = LabeledText(main_pane, "Expected Output", ("Courier New", 11))
        
        top_pane.add(self.code_viewer)
        top_pane.add(self.explanation_text)
        main_pane.add(self.output_text, stretch="never", height=150, minsize=100)

        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        semester = self.controller.current_semester
        level = self.controller.current_level
        path = self.controller.current_path
        if not all([semester, level, path]):
            self.go_back(); return
        
        self.title_label.config(text=f"{level}: {path.capitalize()}")
        all_data = self.controller.get_data()
        self._current_content = all_data.get(semester, {}).get("levels", {}).get(level, {}).get(path, {})
        self.load_content()

        is_dev = self.controller.user_role == "developer"
        widget_state = "normal" if is_dev else "disabled"
        self.code_viewer.set_state(widget_state)
        self.explanation_text.set_state(widget_state)
        self.output_text.set_state(widget_state)

        if is_dev: self.save_button.pack(side="right")
        else: self.save_button.pack_forget()

    def load_content(self):
        self.code_viewer.set(self._current_content.get("code", "// No code available."))
        self.explanation_text.set(self._current_content.get("explanation", "No explanation available."))
        self.output_text.set(self._current_content.get("output", "No output specified."))

    def save_content(self):
        semester = self.controller.current_semester
        level = self.controller.current_level
        path = self.controller.current_path
        
        data = self.controller.get_data()
        data[semester]["levels"][level][path] = {
            "code": self.code_viewer.get(),
            "explanation": self.explanation_text.get(),
            "output": self.output_text.get()
        }
        
        self.controller.save_data(data)
        messagebox.showinfo("Success", "Content saved successfully!", parent=self)
        logging.info(f"Developer saved content for '{semester}' -> '{level}' -> '{path}'")

    def go_back(self):
        self.controller.show_frame("LevelScreen")