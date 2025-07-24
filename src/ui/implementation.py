# File: client/src/ui/implementation.py (Corrected Final Version)

import tkinter as tk
from tkinter import ttk, messagebox
import threading, queue, time, subprocess, os, json, re, logging
import serial

class SyntaxHighlighter:
    def __init__(self, text_widget): self.text = text_widget; self.text.bind('<KeyRelease>', self.on_key_release); self.theme = {'normal': {'foreground': '#FFFFFF', 'background': '#2b2b2b'}, 'keyword': {'foreground': '#CC7832'}, 'comment': {'foreground': '#808080'}, 'string': {'foreground': '#A5C25C'}, 'number': {'foreground': '#6897BB'}, 'preprocessor': {'foreground': '#8A653B'}}; [self.text.tag_configure(tag, **colors) for tag, colors in self.theme.items()]; self.rules = {'preprocessor': r'(#.*?)\n', 'comment': r'(\/\/.*?)\n|(/\*[\s\S]*?\*/)', 'keyword': r'\b(void|int|char|float|double|bool|const|unsigned|long|short|return|if|else|for|while|do|break|continue|struct|class|public|private|protected|new|delete|true|false|HIGH|LOW|OUTPUT|INPUT|pinMode|digitalWrite|analogWrite|delay|setup|loop|uint8_t|uint16_t|uint32_t)\b', 'string': r'(\".*?\")', 'number': r'\b([0-9]+)\b'}
    def on_key_release(self, event=None): self.highlight()
    def highlight(self, event=None):
        start_index, end_index = "1.0", "end"; [self.text.tag_remove(tag, start_index, end_index) for tag in self.theme.keys()]; self.text.tag_add('normal', start_index, end_index); text_content = self.text.get(start_index, end_index)
        for token_type, pattern in self.rules.items():
            for match in re.finditer(pattern, text_content): start, end = match.span(); match_start = f"{start_index}+{start}c"; match_end = f"{start_index}+{end}c"; self.text.tag_add(token_type, match_start, match_end)

class PlatformIOManager:
    def __init__(self, project_path, output_queue): self.project_path = project_path; self.output_queue = output_queue; self.serial_port = None; self.stop_serial_event = threading.Event()
    def _run_command(self, command):
        try:
            process = subprocess.Popen(command, cwd=self.project_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
            for line in iter(process.stdout.readline, ''): self.output_queue.put(('terminal', line))
            process.wait()
            if process.returncode == 0: self.output_queue.put(('terminal', "\n--- SUCCESS ---\n"))
            else: self.output_queue.put(('terminal', f"\n--- FAILED (Code: {process.returncode}) ---\n"))
        except FileNotFoundError: self.output_queue.put(('terminal', "--- ERROR: 'pio' not found. Is PlatformIO in your PATH? ---\n"))
        except Exception as e: self.output_queue.put(('terminal', f"--- ERROR: {e} ---\n"))
        finally: self.output_queue.put(('finished', None))
    def _listen_on_serial(self, upload_port):
        try:
            self.output_queue.put(('serial', f"--- Connecting to {upload_port} ---\n")); self.serial_port = serial.Serial(upload_port, 115200, timeout=1)
            while not self.stop_serial_event.is_set():
                if self.serial_port and self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    if line: self.output_queue.put(('serial', line + '\n'))
                time.sleep(0.05)
        except serial.SerialException as e: self.output_queue.put(('serial', f"--- Serial Error: {e} ---\n"))
        finally:
            if self.serial_port and self.serial_port.is_open: self.serial_port.close(); self.output_queue.put(('serial', "\n--- Serial port closed ---\n"))
    def compile_in_thread(self): threading.Thread(target=self._run_command, args=(['pio', 'run'],), daemon=True).start()
    def upload_in_thread(self): threading.Thread(target=self._run_command, args=(['pio', 'run', '--target', 'upload'],), daemon=True).start()
    def start_serial_monitor(self, port): self.stop_serial_event.clear(); threading.Thread(target=self._listen_on_serial, args=(port,), daemon=True).start()
    def stop_serial_monitor(self): self.stop_serial_event.set()

class ImplementationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0e0e0")
        self.controller = controller
        self.output_queue = queue.Queue(); self.is_process_running = False
        self.is_in_edit_mode = False; self.last_command = ""
        self.pio_project_path = self.controller.get_robotics_project_path()
        self.pio_manager = PlatformIOManager(self.pio_project_path, self.output_queue)
        self.paste_buttons = {}
        self._create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def _create_widgets(self):
        header = tk.Frame(self, bg="#e0e0e0"); controls = tk.Frame(self, bg="#ccc", relief='raised', bd=1)
        header.pack(side='top', fill='x', padx=5, pady=5); controls.pack(side='bottom', fill='x', ipady=5)
        main_v_pane = ttk.PanedWindow(self, orient='vertical'); main_v_pane.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        top_frame = tk.Frame(main_v_pane); bottom_frame = tk.Frame(main_v_pane)
        main_v_pane.add(top_frame, weight=3); main_v_pane.add(bottom_frame, weight=1)
        top_h_pane = ttk.PanedWindow(top_frame, orient='horizontal'); top_h_pane.pack(fill='both', expand=True)
        bottom_h_pane = ttk.PanedWindow(bottom_frame, orient='horizontal'); bottom_h_pane.pack(fill='both', expand=True)
        tk.Button(header, text="← Back", command=self.go_back).pack(side='left')
        tk.Button(header, text="🔄 Refresh", command=self.refresh_content).pack(side="left", padx=5)
        self.header_label = tk.Label(header, font=("Helvetica", 18, "bold"), bg="#e0e0e0"); self.header_label.pack(side='left', padx=20)
        self.dev_edit_button = tk.Button(header, text="✏️ Edit", command=self.enter_edit_mode)
        self.dev_save_button = tk.Button(header, text="💾 Save", command=lambda: self.exit_edit_mode(save=True))
        explorer_frame = self.create_pane_section(top_h_pane, "Project Files")
        self.file_tree = ttk.Treeview(explorer_frame, show="tree"); self.file_tree.pack(fill='both', expand=True)
        self._populate_file_explorer()
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        top_h_pane.add(explorer_frame, weight=1)
        editor_frame = self.create_pane_section(top_h_pane, "Code Editor", 'code', lambda: self.paste_into_widget(self.code_editor))
        self.code_editor = self.create_text_widget(editor_frame, bg="#2b2b2b", fg="#ffffff", font_family="Courier")
        self.highlighter = SyntaxHighlighter(self.code_editor)
        top_h_pane.add(editor_frame, weight=4)
        details_frame = self.create_pane_section(bottom_h_pane, "Implementation Details", 'details', lambda: self.paste_into_widget(self.exp_text))
        self.exp_text = self.create_text_widget(details_frame, wrap='word', font_family="Helvetica")
        bottom_h_pane.add(details_frame, weight=1)
        output_frame = self.create_pane_section(bottom_h_pane, "Output")
        self.output_notebook = ttk.Notebook(output_frame); self.output_notebook.pack(fill='both', expand=True)
        self.serial_monitor = self.create_output_tab(self.output_notebook, "Serial Monitor", "#000000", "#4E9A06")
        self.terminal_output = self.create_output_tab(self.output_notebook, "Build", "#000000", "#FFFFFF")
        bottom_h_pane.add(output_frame, weight=1)
        self.compile_button = tk.Button(controls, text="▶️ Compile", command=self.compile_code)
        self.upload_button = tk.Button(controls, text="⬆️ Upload", command=self.upload_code)
        self.compile_button.pack(side='left', padx=20, pady=5); self.upload_button.pack(side='left', padx=20, pady=5)
        
    def _populate_file_explorer(self):
        for i in self.file_tree.get_children(): self.file_tree.delete(i)
        robotics_path = self.controller.get_robotics_project_path()
        src_dir_path = os.path.join(robotics_path, 'src')
        src_id = self.file_tree.insert('', 'end', 'src', text='src', open=True)
        if os.path.isdir(src_dir_path):
            for filename in sorted(os.listdir(src_dir_path)):
                if filename == 'main.cpp': rel_path = os.path.join('src', filename); self.file_tree.insert(src_id, 'end', text=filename, values=(rel_path,))
        lib_dir_path = os.path.join(robotics_path, 'lib')
        lib_id = self.file_tree.insert('', 'end', 'lib', text='lib', open=True)
        if not os.path.isdir(lib_dir_path): return
        for library_folder_name in sorted(os.listdir(lib_dir_path)):
            library_path = os.path.join(lib_dir_path, library_folder_name)
            if os.path.isdir(library_path):
                lib_folder_id = self.file_tree.insert(lib_id, 'end', text=library_folder_name, open=True)
                for filename in sorted(os.listdir(library_path)):
                    if filename.endswith('.h') or filename.endswith('.cpp'):
                        rel_path = os.path.join('lib', library_folder_name, filename)
                        self.file_tree.insert(lib_folder_id, 'end', text=filename, values=(rel_path,))
        
    def on_file_select(self, event=None):
        if not self.file_tree.selection(): return
        selected_item_id = self.file_tree.selection()[0]
        item_values = self.file_tree.item(selected_item_id, 'values')
        if not item_values or not item_values[0]: return
        file_path = item_values[0]
        if file_path != 'src/main.cpp':
            self.controller.library_file_to_view = file_path
            self.controller.show_frame("LibraryViewerScreen")

    def _prepare_project(self):
        main_cpp_path = os.path.join(self.pio_project_path, 'src', 'main.cpp')
        code_from_editor = self.code_editor.get("1.0", 'end-1c')
        try:
            with open(main_cpp_path, 'w') as f: f.write(code_from_editor)
        except Exception as e: messagebox.showerror("File Error", f"Could not write to main.cpp:\n{e}")

    def on_show_frame(self, event=None):
        if self.controller.current_user and self.controller.current_semester and self.controller.current_level:
            self.controller.save_last_viewed(self.controller.current_semester, self.controller.current_level, "implementation")
        self.load_content()
        self.update_developer_options()
        self.after(100, self.process_output_queue)

    def load_content(self):
        level_name = self.controller.current_level; self.header_label.config(text=f"Implementation: {level_name}")
        impl_data = self.controller.get_data().get(self.controller.current_semester,{}).get("levels",{}).get(level_name,{}).get("implementation",{})
        self.exp_text.config(state='normal'); self.exp_text.delete(1.0,'end'); self.exp_text.insert('end', impl_data.get("explanation",""))
        self.code_editor.config(state='normal'); self.code_editor.delete(1.0,'end'); self.code_editor.insert('end', impl_data.get("code",""))
        if not self.is_in_edit_mode:
            self.exp_text.config(state='disabled')
            if self.controller.current_user and self.controller.current_user.get('role') == "developer":
                 self.code_editor.config(state='disabled')
        self.highlighter.highlight()
        
    def refresh_content(self):
        if self.is_in_edit_mode: messagebox.showwarning("Refresh Blocked", "Please save or cancel your changes before refreshing."); return
        if self.is_process_running: messagebox.showwarning("Refresh Blocked", "Cannot refresh while a process is running."); return
        self.load_content(); messagebox.showinfo("Refreshed", "Implementation content has been updated.")

    def process_output_queue(self):
        try:
            while True:
                msg_type, line = self.output_queue.get_nowait()
                if msg_type == 'finished': self.is_process_running = False; self.update_button_states()
                elif msg_type == 'terminal':
                    self.terminal_output.config(state='normal'); self.terminal_output.insert('end', line); self.terminal_output.see('end'); self.terminal_output.config(state='disabled')
                    if "--- SUCCESS ---" in line and self.last_command == "upload":
                        if self.controller.current_user and self.controller.current_semester and self.controller.current_level:
                            self.controller.mark_level_as_completed(self.controller.current_semester, self.controller.current_level)
                        self.prompt_and_start_monitor()
                elif msg_type == 'serial': self.serial_monitor.config(state='normal'); self.serial_monitor.insert('end', line); self.serial_monitor.see('end'); self.serial_monitor.config(state='disabled')
        except queue.Empty: pass
        finally: self.after(100, self.process_output_queue)

    def prompt_and_start_monitor(self):
        hardcoded_port = "/dev/ttyUSB0"; logging.info(f"Attempting to start serial monitor on hardcoded port: {hardcoded_port}")
        self.output_notebook.select(0); self.pio_manager.start_serial_monitor(hardcoded_port)

    def update_developer_options(self):
        self.dev_edit_button.pack_forget(); self.dev_save_button.pack_forget()
        is_dev = self.controller.current_user and self.controller.current_user.get('role') == "developer"
        if is_dev:
            if self.is_in_edit_mode: self.dev_save_button.pack(side='right', padx=10)
            else: self.dev_edit_button.pack(side='right', padx=10)
        else: self.is_in_edit_mode = False
        self.update_paste_buttons(); self.update_button_states()

    def enter_edit_mode(self): self.is_in_edit_mode = True; self.exp_text.config(state='normal'); self.code_editor.config(state='normal'); self.update_developer_options()

    def exit_edit_mode(self, save=True):
        if save:
            data = self.controller.get_data()
            level_data = data.setdefault(self.controller.current_semester, {}).setdefault("levels", {}).setdefault(self.controller.current_level, {})
            impl = level_data.setdefault('implementation', {}); impl["explanation"] = self.exp_text.get(1.0, 'end-1c'); impl["code"] = self.code_editor.get(1.0, 'end-1c')
            self.controller.save_data(data); messagebox.showinfo("Saved", "Implementation content has been updated.")
        self.is_in_edit_mode = False; self.load_content(); self.update_developer_options()

    def update_button_states(self):
        state = 'disabled' if self.is_process_running or self.is_in_edit_mode else 'normal'
        self.compile_button.config(state=state); self.upload_button.config(state=state)

    def go_back(self):
        self.pio_manager.stop_serial_monitor()
        if self.is_in_edit_mode: self.exit_edit_mode(save=False)
        self.controller.show_frame("LevelScreen")

    def paste_into_widget(self, target_widget):
        can_paste = False
        is_dev = self.controller.current_user and self.controller.current_user.get('role') == 'developer'
        
        if is_dev and self.is_in_edit_mode: can_paste = True
        if not is_dev and target_widget == self.code_editor: can_paste = True
        
        if not can_paste: return
        
        try:
            clipboard_content = self.clipboard_get()
            target_widget.delete("1.0", "end")
            target_widget.insert("end", clipboard_content)
            if target_widget == self.code_editor:
                self.highlighter.highlight()
        except tk.TclError:
            messagebox.showwarning("Paste Error", "Clipboard is empty.")

    def update_paste_buttons(self):
        is_dev_editing = self.controller.current_user and self.controller.current_user.get('role') == "developer" and self.is_in_edit_mode
        for name, button in self.paste_buttons.items():
            if is_dev_editing: button.pack(side='left', padx=10)
            else: button.pack_forget()

    def start_process(self, target_function, command_name):
        if self.is_process_running: messagebox.showwarning("Busy", "A process is already running."); return
        self._prepare_project(); self.is_process_running = True; self.last_command = command_name; self.update_button_states()
        self.output_notebook.select(1); self.terminal_output.config(state='normal'); self.terminal_output.delete(1.0,'end'); self.terminal_output.config(state='disabled')
        target_function()
        
    def compile_code(self): self.start_process(self.pio_manager.compile_in_thread, "compile")
    
    def upload_code(self):
        self.pio_manager.stop_serial_monitor(); time.sleep(0.5)
        self.serial_monitor.config(state='normal'); self.serial_monitor.delete(1.0,'end'); self.serial_monitor.config(state='disabled')
        self.start_process(self.pio_manager.upload_in_thread, "upload")

    def create_pane_section(self, parent, label_text, name=None, paste_command=None):
        frame = tk.Frame(parent, padx=5, pady=5); header_frame = tk.Frame(frame); header_frame.pack(fill='x', anchor='w')
        tk.Label(header_frame, text=label_text, font=("Helvetica", 12, "bold")).pack(side='left')
        if paste_command and name:
            paste_button = tk.Button(header_frame, text="📋", command=paste_command); self.paste_buttons[name] = paste_button
        return frame

    def create_text_widget(self, parent, bg="#ffffff", fg="#000000", font_family="Courier", wrap='none'):
        text_widget = tk.Text(parent, wrap=wrap, state='disabled', font=(font_family, 11), relief='solid', bd=1, bg=bg, fg=fg, insertbackground="white")
        text_widget.pack(fill='both', expand=True, pady=(5,0))
        return text_widget

    def create_output_tab(self, notebook, text, bg, fg):
        frame = tk.Frame(notebook, bg=bg); text_widget = tk.Text(frame, bg=bg, fg=fg, state='disabled', font=("Courier", 10))
        text_widget.pack(fill='both', expand=True); notebook.add(frame, text=text)
        return text_widget