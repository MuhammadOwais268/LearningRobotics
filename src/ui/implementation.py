# File: src/ui/implementation.py (with Hardcoded Serial Port)

import tkinter as tk
from tkinter import ttk, messagebox
import threading, queue, time, subprocess, os, json, re, logging
import serial

# ==============================================================================
# SyntaxHighlighter Class (Unchanged)
# ==============================================================================
class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text = text_widget
        self.text.bind('<KeyRelease>', self.on_key_release)
        self.theme = {
            'normal': {'foreground': '#FFFFFF', 'background': '#2b2b2b'},
            'keyword': {'foreground': '#CC7832'}, 'comment': {'foreground': '#808080'},
            'string': {'foreground': '#A5C25C'}, 'number': {'foreground': '#6897BB'},
            'preprocessor': {'foreground': '#8A653B'},
        }
        for tag, colors in self.theme.items(): self.text.tag_configure(tag, **colors)
        self.rules = {
            'preprocessor': r'(#.*?)\n', 'comment': r'(\/\/.*?)\n|(/\*[\s\S]*?\*/)',
            'keyword': r'\b(void|int|char|float|double|bool|const|unsigned|long|short|return|if|else|for|while|do|break|continue|struct|class|public|private|protected|new|delete|true|false|HIGH|LOW|OUTPUT|INPUT|pinMode|digitalWrite|analogWrite|delay|setup|loop|uint8_t|uint16_t|uint32_t)\b',
            'string': r'(\".*?\")', 'number': r'\b([0-9]+)\b',
        }
    def on_key_release(self, event=None): self.highlight()
    def highlight(self, event=None):
        start_index, end_index = "1.0", "end"
        for tag in self.theme.keys(): self.text.tag_remove(tag, start_index, end_index)
        self.text.tag_add('normal', start_index, end_index)
        text_content = self.text.get(start_index, end_index)
        for token_type, pattern in self.rules.items():
            for match in re.finditer(pattern, text_content):
                start, end = match.span()
                match_start = f"{start_index}+{start}c"; match_end = f"{start_index}+{end}c"
                self.text.tag_add(token_type, match_start, match_end)

# ==============================================================================
# PlatformIOManager Class (Unchanged)
# ==============================================================================
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
            self.output_queue.put(('serial', f"--- Connecting to {upload_port} ---\n"))
            self.serial_port = serial.Serial(upload_port, 115200, timeout=1)
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

# ==============================================================================
# ImplementationScreen Class (Modified to use the highlighter)
# ==============================================================================
class ImplementationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0e0e0")
        self.controller = controller
        self.output_queue = queue.Queue(); self.is_process_running = False; self.is_in_edit_mode = False; self.last_command = ""
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.pio_project_path = os.path.join(project_root, '..', 'Robotics')
        self.pio_manager = PlatformIOManager(self.pio_project_path, self.output_queue)
        self.paste_buttons = []
        self._create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event=None):
        self.load_content()
        self.update_developer_options()
        self.after(100, self.process_output_queue)

    def process_output_queue(self):
        try:
            while True:
                msg_type, line = self.output_queue.get_nowait()
                if msg_type == 'finished': self.is_process_running = False; self.update_button_states()
                elif msg_type == 'terminal':
                    self.terminal_output.config(state='normal'); self.terminal_output.insert('end', line); self.terminal_output.see('end'); self.terminal_output.config(state='disabled')
                    if "--- SUCCESS ---" in line and self.last_command == "upload":
                        # This is the trigger for our new feature
                        self.prompt_and_start_monitor()
                elif msg_type == 'serial':
                    self.serial_monitor.config(state='normal'); self.serial_monitor.insert('end', line); self.serial_monitor.see('end'); self.serial_monitor.config(state='disabled')
        except queue.Empty: pass
        finally: self.after(100, self.process_output_queue)

    # =================================================================
    # <<< THIS METHOD HAS BEEN MODIFIED >>>
    # =================================================================
    def prompt_and_start_monitor(self):
        """
        This version bypasses automatic device detection and forces a connection
        to the hardcoded port '/dev/ttyUSB0'.
        """
        # Define the specific port you always want to use.
        hardcoded_port = "/dev/ttyUSB0"
        
        logging.info(f"Attempting to start serial monitor on hardcoded port: {hardcoded_port}")
        
        # Switch the UI to the Serial Monitor tab automatically.
        self.output_notebook.select(0) 
        
        # Directly call the pio_manager to start listening on the specified port.
        # The manager's built-in error handling will catch if the port doesn't exist or is busy.
        self.pio_manager.start_serial_monitor(hardcoded_port)

    # This method is no longer used, but we'll keep it for future reference.
    def show_port_selection_dialog(self, devices):
        dialog = tk.Toplevel(self); dialog.title("Select Port"); dialog.geometry("400x150"); dialog.transient(self); dialog.grab_set()
        tk.Label(dialog, text="Multiple devices found.\nPlease select the correct port to monitor:", pady=10).pack()
        port_options = [f"{d['port']} ({d.get('description', 'No description')})" for d in devices]
        port_map = {f"{d['port']} ({d.get('description', 'No description')})": d['port'] for d in devices}
        combobox = ttk.Combobox(dialog, values=port_options, state="readonly", width=50); combobox.pack(pady=5, padx=10); combobox.current(0)
        def on_connect():
            selection = combobox.get()
            if selection: port_to_connect = port_map[selection]; dialog.destroy(); self.output_notebook.select(0); self.pio_manager.start_serial_monitor(port_to_connect)
        btn_frame = tk.Frame(dialog); btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Connect", command=on_connect).pack(side='left', padx=10); tk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=10)

    # --- The rest of the file is unchanged from the last correct version ---
    def _create_widgets(self):
        header = tk.Frame(self, bg="#e0e0e0"); main = tk.Frame(self, bg="white"); controls = tk.Frame(self, bg="#ccc", relief='raised', bd=1)
        header.pack(side='top', fill='x', padx=5, pady=5); controls.pack(side='bottom', fill='x', ipady=5); main.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        tk.Button(header, text="← Back", command=self.go_back).pack(side='left'); tk.Button(header, text="🔄 Refresh", command=self.refresh_content).pack(side="left", padx=5)
        self.header_label = tk.Label(header, font=("Helvetica", 18, "bold"), bg="#e0e0e0"); self.header_label.pack(side='left', padx=20)
        self.dev_edit_button = tk.Button(header, text="✏️ Edit Content", command=self.enter_edit_mode)
        self.dev_save_button = tk.Button(header, text="💾 Save Changes", command=lambda: self.exit_edit_mode(save=True))
        v_pane = ttk.PanedWindow(main, orient='vertical'); v_pane.pack(fill='both', expand=True)
        top_frame = tk.Frame(v_pane); h_pane = ttk.PanedWindow(top_frame, orient='horizontal'); h_pane.pack(fill='both', expand=True); v_pane.add(top_frame, weight=3)
        code_frame = self.create_pane_section(h_pane, "Implementation Code", paste_command=lambda: self.paste_into_widget(self.code_editor))
        self.code_editor = self.create_text_widget(code_frame, bg="#2b2b2b", fg="#ffffff", font_family="Courier")
        self.highlighter = SyntaxHighlighter(self.code_editor)
        h_pane.add(code_frame, weight=2)
        exp_frame = self.create_pane_section(h_pane, "Implementation Details", paste_command=lambda: self.paste_into_widget(self.exp_text))
        self.exp_text = self.create_text_widget(exp_frame, wrap='word', font_family="Helvetica"); h_pane.add(exp_frame, weight=1)
        output_notebook = ttk.Notebook(v_pane); v_pane.add(output_notebook, weight=1)
        self.serial_monitor = self.create_output_tab(output_notebook, "Serial Monitor", "#000000", "#4E9A06")
        self.terminal_output = self.create_output_tab(output_notebook, "Terminal Output", "#000000", "#FFFFFF"); self.output_notebook = output_notebook
        self.compile_button = tk.Button(controls, text="▶️ Compile", command=self.compile_code); self.upload_button = tk.Button(controls, text="⬆️ Upload", command=self.upload_code)
        self.compile_button.pack(side='left', padx=20, pady=5); self.upload_button.pack(side='left', padx=20, pady=5)
    def load_content(self):
        level_name = self.controller.current_level; self.header_label.config(text=f"Implementation: {level_name}")
        impl_data = self.controller.get_data().get(self.controller.current_semester,{}).get("levels",{}).get(level_name,{}).get("implementation",{})
        self.exp_text.config(state='normal'); self.code_editor.config(state='normal')
        self.exp_text.delete(1.0,'end'); self.code_editor.delete(1.0,'end')
        self.exp_text.insert('end', impl_data.get("explanation","")); self.code_editor.insert('end', impl_data.get("code",""))
        if not self.is_in_edit_mode: self.exp_text.config(state='disabled'); self.code_editor.config(state='disabled')
        self.highlighter.highlight()
    def refresh_content(self):
        if self.is_in_edit_mode: messagebox.showwarning("Refresh Blocked", "Please save or cancel your changes before refreshing."); return
        if self.is_process_running: messagebox.showwarning("Refresh Blocked", "Cannot refresh while a process is running."); return
        self.load_content(); messagebox.showinfo("Refreshed", "Implementation content has been updated.")
    def update_developer_options(self):
        self.dev_edit_button.pack_forget(); self.dev_save_button.pack_forget()
        is_dev = self.controller.current_user.get('role') == "developer"
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
            impl = level_data.setdefault('implementation', {})
            impl["explanation"] = self.exp_text.get(1.0, 'end-1c'); impl["code"] = self.code_editor.get(1.0, 'end-1c')
            self.controller.save_data(data); messagebox.showinfo("Saved", "Implementation content has been updated.")
        self.is_in_edit_mode = False; self.exp_text.config(state='disabled'); self.code_editor.config(state='disabled'); self.update_developer_options()
    def update_button_states(self):
        state = 'disabled' if self.is_process_running or self.is_in_edit_mode else 'normal'
        self.compile_button.config(state=state); self.upload_button.config(state=state)
    def go_back(self):
        self.pio_manager.stop_serial_monitor()
        if self.is_in_edit_mode: self.exit_edit_mode(save=False)
        self.controller.show_frame("LevelScreen")
    def paste_into_widget(self, target_widget):
        if not self.is_in_edit_mode: return
        try:
            clipboard_content = self.clipboard_get()
            if target_widget == self.code_editor: target_widget.delete(1.0, 'end'); target_widget.insert('end', clipboard_content); self.highlighter.highlight()
            else: target_widget.delete(1.0, 'end'); target_widget.insert('end', clipboard_content)
        except tk.TclError: messagebox.showwarning("Paste Error", "Clipboard is empty.")
    def update_paste_buttons(self):
        is_dev_editing = self.controller.current_user.get('role') == "developer" and self.is_in_edit_mode
        for paste_button in self.paste_buttons:
            if is_dev_editing: paste_button.pack(side='left', padx=10)
            else: paste_button.pack_forget()
    def _prepare_project(self):
        code = self.code_editor.get(1.0, 'end-1c'); src_path = os.path.join(self.pio_project_path, 'src')
        os.makedirs(src_path, exist_ok=True)
        with open(os.path.join(src_path, 'main.cpp'), 'w') as f: f.write(code)
    def start_process(self, target_function, command_name):
        if self.is_process_running: messagebox.showwarning("Busy", "A process is already running."); return
        self._prepare_project(); self.is_process_running = True; self.last_command = command_name; self.update_button_states()
        self.terminal_output.config(state='normal'); self.terminal_output.delete(1.0,'end'); self.terminal_output.config(state='disabled')
        self.output_notebook.select(1); target_function()
    def compile_code(self): self.start_process(self.pio_manager.compile_in_thread, "compile")
    def upload_code(self):
        self.pio_manager.stop_serial_monitor(); time.sleep(0.5)
        self.serial_monitor.config(state='normal'); self.serial_monitor.delete(1.0,'end'); self.serial_monitor.config(state='disabled')
        self.start_process(self.pio_manager.upload_in_thread, "upload")
    def create_pane_section(self, parent, label_text, paste_command=None):
        frame = tk.Frame(parent, padx=5, pady=5); header_frame = tk.Frame(frame); header_frame.pack(fill='x', anchor='w')
        tk.Label(header_frame, text=label_text, font=("Helvetica", 14, "bold")).pack(side='left')
        if paste_command: paste_button = tk.Button(header_frame, text="📋 Paste", command=paste_command); self.paste_buttons.append(paste_button)
        return frame
    def create_text_widget(self, parent, bg="#ffffff", fg="#000000", font_family="Courier", wrap='none'):
        text_widget = tk.Text(parent, wrap=wrap, state='disabled', font=(font_family, 11), relief='solid', bd=1, bg=bg, fg=fg, insertbackground=fg)
        text_widget.pack(fill='both', expand=True, pady=(5,0))
        return text_widget
    def create_output_tab(self, notebook, text, bg, fg):
        frame = tk.Frame(notebook, bg=bg); text_widget = tk.Text(frame, bg=bg, fg=fg, state='disabled', font=("Courier", 10))
        text_widget.pack(fill='both', expand=True); notebook.add(frame, text=text)
        return text_widget