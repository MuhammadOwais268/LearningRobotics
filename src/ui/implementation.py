# File: /home/owais/LearningRobotics/src/ui/implementation.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading, queue, time, subprocess, os, json
import serial
import logging

class PlatformIOManager:
    def __init__(self, project_path, output_queue):
        self.project_path = project_path
        self.output_queue = output_queue
        self.serial_port = None
        self.stop_serial_event = threading.Event()

    def _run_command(self, command):
        try:
            process = subprocess.Popen(command, cwd=self.project_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
            for line in iter(process.stdout.readline, ''):
                self.output_queue.put(('terminal', line))
            process.wait()
            if process.returncode == 0: self.output_queue.put(('terminal', "\n--- SUCCESS ---\n"))
            else: self.output_queue.put(('terminal', f"\n--- FAILED (Code: {process.returncode}) ---\n"))
        except FileNotFoundError: self.output_queue.put(('terminal', "--- ERROR: 'pio' not found. Is PlatformIO in your PATH? ---\n"))
        except Exception as e: self.output_queue.put(('terminal', f"--- ERROR: {e} ---\n"))
        finally: self.output_queue.put(('finished', None))

    def _listen_on_serial(self, upload_port):
        try:
            self.output_queue.put(('serial', f"--- Connecting to {upload_port} ---\n"))
            self.serial_port = serial.Serial(upload_port, 9600, timeout=1)
            while not self.stop_serial_event.is_set():
                if self.serial_port and self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    if line: self.output_queue.put(('serial', line + '\n'))
                else:
                    time.sleep(0.05)
        except serial.SerialException as e:
            self.output_queue.put(('serial', f"--- Serial Error: {e} ---\n"))
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                self.output_queue.put(('serial', "\n--- Serial port closed ---\n"))

    def compile_in_thread(self): threading.Thread(target=self._run_command, args=(['pio', 'run'],), daemon=True).start()
    def upload_in_thread(self): threading.Thread(target=self._run_command, args=(['pio', 'run', '--target', 'upload'],), daemon=True).start()
    def start_serial_monitor(self, port): self.stop_serial_event.clear(); threading.Thread(target=self._listen_on_serial, args=(port,), daemon=True).start()
    def stop_serial_monitor(self): self.stop_serial_event.set()

class ImplementationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0e0e0")
        self.controller = controller
        self.output_queue = queue.Queue()
        self.is_process_running = False
        self.is_in_edit_mode = False
        
        self.last_command = ""
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.pio_project_path = os.path.join(project_root, '..', '..', 'Robotics')
        self.pio_manager = PlatformIOManager(self.pio_project_path, self.output_queue)
        self.paste_buttons = []
        self._create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event=None):
        self.load_content()
        self.update_developer_options()
        self.after(100, self.process_output_queue)

    def go_back(self):
        self.pio_manager.stop_serial_monitor()
        if self.is_in_edit_mode:
            self.exit_edit_mode(save=False)
        self.controller.show_frame("LevelScreen")

    def _prepare_project(self):
        code = self.code_editor.get(1.0, 'end-1c')
        src_path = os.path.join(self.pio_project_path, 'src')
        os.makedirs(src_path, exist_ok=True)
        with open(os.path.join(src_path, 'main.cpp'), 'w') as f:
            f.write(code)

    def start_process(self, target_function, command_name):
        if self.is_process_running:
            messagebox.showwarning("Busy", "A process is already running.")
            return
        
        self._prepare_project()
        self.is_process_running = True
        self.last_command = command_name
        self.update_button_states()

        self.terminal_output.config(state='normal')
        self.terminal_output.delete(1.0, 'end')
        self.terminal_output.config(state='disabled')
        self.output_notebook.select(1)
        
        target_function()

    def compile_code(self):
        self.start_process(self.pio_manager.compile_in_thread, "compile")

    def upload_code(self):
        self.pio_manager.stop_serial_monitor()
        time.sleep(0.5)
        self.serial_monitor.config(state='normal')
        self.serial_monitor.delete(1.0, 'end')
        self.serial_monitor.config(state='disabled')
        self.start_process(self.pio_manager.upload_in_thread, "upload")

    def process_output_queue(self):
        try:
            while True:
                msg_type, line = self.output_queue.get_nowait()
                
                if msg_type == 'finished':
                    self.is_process_running = False
                    self.update_button_states()
                
                elif msg_type == 'terminal':
                    self.terminal_output.config(state='normal')
                    self.terminal_output.insert('end', line)
                    self.terminal_output.see('end')
                    self.terminal_output.config(state='disabled')

                    if "--- SUCCESS ---" in line and self.last_command == "upload":
                        try:
                            cmd = ['pio', 'device', 'list', '--json-output', '--serial']
                            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.pio_project_path)
                            devices = json.loads(result.stdout)
                            port = devices[0]['port']
                            self.output_notebook.select(0)
                            self.pio_manager.start_serial_monitor(port)
                        except (IndexError, json.JSONDecodeError):
                            self.serial_monitor.config(state='normal')
                            self.serial_monitor.insert('end', "Upload successful, but could not find a serial port to monitor.")
                            self.serial_monitor.config(state='disabled')

                elif msg_type == 'serial':
                    self.serial_monitor.config(state='normal')
                    self.serial_monitor.insert('end', line)
                    self.serial_monitor.see('end')
                    self.serial_monitor.config(state='disabled')
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_output_queue)

    def _create_widgets(self):
        header = tk.Frame(self, bg="#e0e0e0")
        main = tk.Frame(self, bg="white")
        controls = tk.Frame(self, bg="#ccc", relief='raised', bd=1)
        header.pack(side='top', fill='x', padx=5, pady=5)
        controls.pack(side='bottom', fill='x', ipady=5)
        main.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        
        tk.Button(header, text="← Back", command=self.go_back).pack(side='left')
        self.header_label = tk.Label(header, font=("Helvetica", 18, "bold"), bg="#e0e0e0")
        self.header_label.pack(side='left', padx=20)
        
        self.dev_edit_button = tk.Button(header, text="✏️ Edit Content", command=self.enter_edit_mode)
        self.dev_save_button = tk.Button(header, text="💾 Save Changes", command=self.exit_edit_mode)

        v_pane = ttk.PanedWindow(main, orient='vertical')
        v_pane.pack(fill='both', expand=True)
        top_frame = tk.Frame(v_pane)
        h_pane = ttk.PanedWindow(top_frame, orient='horizontal')
        h_pane.pack(fill='both', expand=True)
        v_pane.add(top_frame, weight=3)
        
        code_frame = self.create_pane_section(
            h_pane, 
            "Implementation Code", 
            paste_command=lambda: self.paste_into_widget(self.code_editor)
        )
        self.code_editor = self.create_text_widget(code_frame, bg="#2b2b2b", fg="#ffffff", font_family="Courier")
        h_pane.add(code_frame, weight=2)
        
        exp_frame = self.create_pane_section(
            h_pane, 
            "Implementation Details", 
            paste_command=lambda: self.paste_into_widget(self.exp_text)
        )
        self.exp_text = self.create_text_widget(exp_frame, wrap='word', font_family="Helvetica")
        h_pane.add(exp_frame, weight=1)
        
        output_notebook = ttk.Notebook(v_pane)
        v_pane.add(output_notebook, weight=1)
        self.serial_monitor = self.create_output_tab(output_notebook, "Serial Monitor", "#000000", "#4E9A06")
        self.terminal_output = self.create_output_tab(output_notebook, "Terminal Output", "#000000", "#FFFFFF")
        self.output_notebook = output_notebook

        self.compile_button = tk.Button(controls, text="▶️ Compile", command=self.compile_code)
        self.upload_button = tk.Button(controls, text="⬆️ Upload", command=self.upload_code)
        self.compile_button.pack(side='left', padx=20, pady=5)
        self.upload_button.pack(side='left', padx=20, pady=5)

    def load_content(self):
        if not self.controller.current_semester or not self.controller.current_level:
            messagebox.showerror("Error", "No semester or level selected.")
            return
        level_name = self.controller.current_level
        self.header_label.config(text=f"Implementation: {level_name}")
        data = self.controller.get_data()
        logging.info(f"Loading implementation data: {data}")
        semester_data = data.get(self.controller.current_semester, {})
        level_data = semester_data.get("levels", {}).get(level_name, {})
        impl_data = level_data.get("implementation", {"explanation": "", "code": ""})
        
        self.exp_text.config(state='normal')
        self.code_editor.config(state='normal')
        self.exp_text.delete(1.0, 'end')
        self.code_editor.delete(1.0, 'end')
        self.exp_text.insert('end', impl_data.get("explanation", ""))
        self.code_editor.insert('end', impl_data.get("code", ""))
        if not self.is_in_edit_mode:
            self.exp_text.config(state='disabled')
            self.code_editor.config(state='disabled')

    def update_button_states(self):
        state = 'disabled' if self.is_process_running or self.is_in_edit_mode else 'normal'
        self.compile_button.config(state=state)
        self.upload_button.config(state=state)

    def enter_edit_mode(self):
        self.is_in_edit_mode = True
        self.exp_text.config(state='normal')
        self.code_editor.config(state='normal')
        self.dev_edit_button.pack_forget()
        self.dev_save_button.pack(side='right', padx=10)
        self.update_button_states()
        self.update_paste_buttons()

    def exit_edit_mode(self, save=True):
        if not self.controller.current_semester or not self.controller.current_level:
            messagebox.showerror("Error", "No semester or level selected.")
            return
        if save:
            data = self.controller.get_data()
            logging.info(f"Saving implementation data: {data}")
            semester_data = data.setdefault(self.controller.current_semester, {})
            levels_data = semester_data.setdefault("levels", {})
            level_data = levels_data.setdefault(self.controller.current_level, {})
            impl = level_data.setdefault("implementation", {"explanation": "", "code": ""})
            
            impl["explanation"] = self.exp_text.get(1.0, 'end-1c')
            impl["code"] = self.code_editor.get(1.0, 'end-1c')
            try:
                self.controller.save_data(data)
                messagebox.showinfo("Saved", "Implementation content has been updated.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")
                return

        self.is_in_edit_mode = False
        self.exp_text.config(state='disabled')
        self.code_editor.config(state='disabled')
        self.dev_save_button.pack_forget()
        self.dev_edit_button.pack(side='right', padx=10)
        self.update_button_states()
        self.update_paste_buttons()

    def update_developer_options(self):
        self.dev_edit_button.pack_forget()
        self.dev_save_button.pack_forget()

        if self.controller.user_role == "developer":
            if self.is_in_edit_mode:
                self.dev_save_button.pack(side='right', padx=10)
            else:
                self.dev_edit_button.pack(side='right', padx=10)
        
        self.update_paste_buttons()

    def create_pane_section(self, parent, label_text, paste_command=None):
        frame = tk.Frame(parent, padx=5, pady=5)
        header_frame = tk.Frame(frame)
        header_frame.pack(fill='x', anchor='w')

        tk.Label(header_frame, text=label_text, font=("Helvetica", 14, "bold")).pack(side='left')

        if paste_command:
            paste_button = tk.Button(header_frame, text="📋 Paste", command=paste_command)
            self.paste_buttons.append(paste_button)
            paste_button.pack_forget()

        return frame

    def update_paste_buttons(self):
        for paste_button in self.paste_buttons:
            paste_button.pack_forget()
            if self.controller.user_role == "developer" and self.is_in_edit_mode:
                paste_button.pack(side='left', padx=10)

    def paste_into_widget(self, target_widget):
        if not self.is_in_edit_mode:
            messagebox.showinfo("Read-Only Mode", "Please click '✏️ Edit Content' before pasting.")
            return
        
        try:
            clipboard_content = self.clipboard_get()
            target_widget.delete(1.0, 'end')
            target_widget.insert('end', clipboard_content)
        except tk.TclError:
            messagebox.showwarning("Paste Error", "Could not get text from clipboard. It might be empty or contain invalid content.")

    def create_text_widget(self, parent, bg="#ffffff", fg="#000000", font_family="Courier", wrap='none'):
        text_widget = tk.Text(parent, wrap=wrap, state='disabled', font=(font_family, 11), relief='solid', bd=1, bg=bg, fg=fg, insertbackground=fg)
        text_widget.pack(fill='both', expand=True, pady=(5, 0))
        return text_widget

    def create_output_tab(self, notebook, text, bg, fg):
        frame = tk.Frame(notebook, bg=bg)
        text_widget = tk.Text(frame, bg=bg, fg=fg, state='disabled', font=("Courier", 10))
        text_widget.pack(fill='both', expand=True)
        notebook.add(frame, text=text)
        return text_widget