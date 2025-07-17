# File: ui/implementation.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading, queue, time

# This mock function simulates running PlatformIO.
def run_mock_process(command, output_queue):
    output_queue.put(f"> Executing: {command}\n")
    time.sleep(1)
    output_queue.put("Compiling source files...\n")
    time.sleep(1.5)
    output_queue.put("Linking firmware...\n")
    time.sleep(1)
    if "upload" in command:
        output_queue.put("Connecting to port... \n")
        time.sleep(1)
        output_queue.put("Uploading firmware...\n")
        time.sleep(2)
    output_queue.put("--- SUCCESS ---\n")
    output_queue.put(None) # Signal that the process is finished

class ImplementationScreen(tk.Frame):
    """
    Shows a specific, compilable implementation of a concept
    with interactive Compile and Upload buttons.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0e0e0")
        self.controller = controller
        self.output_queue = queue.Queue()
        self.is_process_running = False
        self.is_dev_editing = False
        self._create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event=None):
        self.load_content()
        self.update_developer_options()
        self.after(100, self.process_output_queue)

    def _create_widgets(self):
        # FIXED: Used full words for side, fill, etc.
        header = tk.Frame(self, bg="#e0e0e0")
        main = tk.Frame(self, bg="white")
        controls = tk.Frame(self, bg="#cccccc", relief='raised', bd=1)
        header.pack(side='top', fill='x', padx=5, pady=5)
        controls.pack(side='bottom', fill='x', ipady=5)
        main.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        
        tk.Button(header, text="← Back to Levels", command=self.go_back).pack(side='left')
        self.header_label = tk.Label(header, text="Implementation:", font=("Helvetica", 18, "bold"), bg="#e0e0e0")
        self.header_label.pack(side='left', padx=20)
        self.dev_edit_button = tk.Button(header, text="✏️ Edit Implementation", command=self.toggle_dev_edit_mode)

        v_pane = ttk.PanedWindow(main, orient='vertical'); v_pane.pack(fill='both', expand=True)
        top_frame = tk.Frame(v_pane); h_pane = ttk.PanedWindow(top_frame, orient='horizontal'); h_pane.pack(fill='both', expand=True); v_pane.add(top_frame, weight=3)
        
        exp_frame = self.create_pane_section(h_pane, "Implementation Details"); self.exp_text = self.create_text_widget(exp_frame, wrap='word', font_family="Helvetica"); h_pane.add(exp_frame, weight=1)
        code_frame = self.create_pane_section(h_pane, "Implementation Code"); self.code_editor = self.create_text_widget(code_frame, bg="#2b2b2b", fg="white", font_family="Courier"); h_pane.add(code_frame, weight=2)
        
        output_notebook = ttk.Notebook(v_pane); v_pane.add(output_notebook, weight=1)
        self.serial_monitor = self.create_output_tab(output_notebook, "Serial Monitor", "#000000", "#4E9A06")
        self.terminal_output = self.create_output_tab(output_notebook, "Terminal Output", "#000000", "#FFFFFF")
        self.output_notebook = output_notebook

        self.compile_button = tk.Button(controls, text="▶️ Compile", command=self.compile_code)
        self.upload_button = tk.Button(controls, text="⬆️ Upload", command=self.upload_code)
        self.compile_button.pack(side='left', padx=20, pady=5)
        self.upload_button.pack(side='left', padx=20, pady=5)

    def load_content(self):
        level_name = self.controller.current_level
        self.header_label.config(text=f"Implementation: {level_name}")
        impl_data = self.controller.get_data().get(self.controller.current_semester,{}).get("levels",{}).get(level_name,{}).get("implementation",{})
        for w, k in [(self.exp_text, "explanation"), (self.code_editor, "code")]:
            w.config(state='normal'); w.delete(1.0,'end'); w.insert('end',impl_data.get(k,"")); w.config(state='disabled')

    def compile_code(self): self.start_process("pio run")
    def upload_code(self): self.start_process("pio run --target upload")
    
    def start_process(self, command):
        if self.is_process_running: return
        self.is_process_running = True; self.update_button_states()
        self.terminal_output.config(state='normal'); self.terminal_output.delete(1.0,'end'); self.terminal_output.config(state='disabled')
        self.output_notebook.select(1)
        threading.Thread(target=run_mock_process, args=(command, self.output_queue), daemon=True).start()

    def process_output_queue(self):
        try:
            line = self.output_queue.get_nowait()
            if line is None: self.is_process_running = False; self.update_button_states()
            else: self.terminal_output.config(state='normal');self.terminal_output.insert('end',line);self.terminal_output.see('end');self.terminal_output.config(state='disabled')
        except queue.Empty: pass
        self.after(100, self.process_output_queue)

    def update_button_states(self):
        state = 'disabled' if self.is_process_running or self.is_dev_editing else 'normal'
        self.compile_button.config(state=state)
        self.upload_button.config(state=state)

    def toggle_dev_edit_mode(self):
        self.is_dev_editing = not self.is_dev_editing
        state, text = ('normal', "💾 Save") if self.is_dev_editing else ('disabled', "✏️ Edit Implementation")
        self.dev_edit_button.config(text=text)
        self.exp_text.config(state=state); self.code_editor.config(state=state)
        self.update_button_states()
        if not self.is_dev_editing:
            data = self.controller.get_data()
            impl = data[self.controller.current_semester]["levels"][self.controller.current_level]["implementation"]
            impl["explanation"] = self.exp_text.get(1.0, 'end-1c'); impl["code"] = self.code_editor.get(1.0, 'end-1c')
            self.controller.save_data(data); messagebox.showinfo("Saved", "Implementation content updated.")

    def update_developer_options(self):
        if self.controller.user_role == "developer": self.dev_edit_button.pack(side='right', padx=10)
        else: self.dev_edit_button.pack_forget()
        if self.is_dev_editing: self.toggle_dev_edit_mode()

    def go_back(self): self.controller.show_frame("LevelScreen")
    
    # --- CORRECTED HELPER METHODS ---
    def create_pane_section(self,parent,label_text):
        frame=tk.Frame(parent,padx=5,pady=5)
        tk.Label(frame,text=label_text,font=("Helvetica",14,"bold")).pack(anchor='w')
        return frame
        
    def create_text_widget(self,parent,bg="#ffffff",fg="#000000",font_family="Courier",wrap='none'):
        text_widget=tk.Text(parent,wrap=wrap,state='disabled',font=(font_family,11),relief='solid',bd=1,bg=bg,fg=fg)
        text_widget.pack(fill='both',expand=True,pady=(5,0))
        return text_widget
        
    def create_output_tab(self,notebook,text,bg,fg):
        frame=tk.Frame(notebook,bg=bg)
        text_widget=tk.Text(frame,bg=bg,fg=fg,state='disabled',font=("Courier",10))
        text_widget.pack(fill='both',expand=True)
        notebook.add(frame,text=text)
        return text_widget