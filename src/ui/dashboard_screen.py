# File: client/src/ui/dashboard_screen.py (Corrected to Show History)

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class DashboardScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller

        self.last_viewed = {}
        self.next_up = {}
        self.history_visible = False

        self._create_widgets()
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def _create_widgets(self):
        # --- Header ---
        header_frame = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        header_frame.pack(fill='x', side='top') # Use side='top'
        self.header_label = tk.Label(header_frame, text="Dashboard", font=("Helvetica", 24, "bold"), bg="#f4f6f7")
        self.header_label.pack(side='left')
        tk.Button(header_frame, text="View Full Curriculum →", command=self.view_full_curriculum).pack(side='right')

        # Main content area - This will hold all the cards
        self.content_frame = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        self.content_frame.pack(fill='both', expand=True, side='top') # Use side='top'

        # --- Section 1: Continue ---
        self.continue_section_frame = self.create_section_frame(self.content_frame, "CONTINUE WHERE YOU LEFT OFF")
        self.last_viewed_label = tk.Label(self.continue_section_frame, text="No history yet.", font=("Helvetica", 14), bg="white")
        self.last_viewed_label.pack(side='left', padx=20, pady=10)
        self.go_to_button = tk.Button(self.continue_section_frame, text="Go to >", command=self.go_to_last_viewed)
        self.go_to_button.pack(side='right', padx=20, pady=10)

        # --- Section 2: Progress ---
        self.progress_section_frame = self.create_section_frame(self.content_frame, "YOUR PROGRESS")
        self.progress_text_label = tk.Label(self.progress_section_frame, text="0 / 0 Levels Completed", font=("Helvetica", 12), bg="white")
        self.progress_text_label.pack(pady=(10, 5))
        progress_bar_frame = tk.Frame(self.progress_section_frame, bg="white")
        progress_bar_frame.pack(fill='x', expand=True, padx=20, pady=10)
        self.progress_bar = ttk.Progressbar(progress_bar_frame, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(side='left', fill='x', expand=True)
        self.progress_percent_label = tk.Label(progress_bar_frame, text="0%", font=("Helvetica", 12), bg="white")
        self.progress_percent_label.pack(side='left', padx=10)
        
        self.history_button = tk.Button(self.progress_section_frame, text="View History ▼", command=self.toggle_history)
        self.history_button.pack(pady=(5, 10))

        # --- Section 2a: History Frame (Initially Hidden) ---
        self.history_frame = tk.Frame(self.content_frame, bg="#e0e0e0", bd=1, relief='solid')
        # We do NOT .pack() it here.
        tk.Label(self.history_frame, text="✓ = Completed (Uploaded)", bg="#e0e0e0", justify='left').pack(anchor='w', padx=10, pady=(5,0))
        # This frame will be populated with the list of levels
        self.history_list_frame = tk.Frame(self.history_frame, bg="white")
        self.history_list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # --- Section 3: Next Up ---
        self.next_up_section_frame = self.create_section_frame(self.content_frame, "WHAT'S NEXT")
        self.next_up_label = tk.Label(self.next_up_section_frame, text="All done!", font=("Helvetica", 14), bg="white")
        self.next_up_label.pack(side='left', padx=20, pady=10)
        self.start_next_button = tk.Button(self.next_up_section_frame, text="Start >", command=self.start_next_level)
        self.start_next_button.pack(side='right', padx=20, pady=10)
        
        # --- Footer ---
        footer_frame = tk.Frame(self, bg="#f4f6f7", padx=20, pady=10)
        footer_frame.pack(fill='x', side='bottom')
        tk.Button(footer_frame, text="Logout", fg="red", command=self.controller.logout).pack(side='right')
        tk.Button(footer_frame, text="Reset Progress", command=self.confirm_and_reset_progress).pack(side='right', padx=10)
        tk.Button(footer_frame, text="Change Mode", command=self.change_mode).pack(side='right', padx=10)

    def on_show_frame(self, event=None):
        self.history_visible = False # Always start with history hidden
        self.history_frame.pack_forget() # Ensure it's hidden
        self.history_button.config(text="View History ▼")
        self.update_dashboard()
        
    def toggle_history(self):
        """Shows or hides the history frame."""
        self.history_visible = not self.history_visible
        if self.history_visible:
            self.populate_history()
            # <<< FIX: Use .pack() with 'after' to insert it in the correct place >>>
            self.history_frame.pack(fill='x', pady=10, padx=20, after=self.progress_section_frame)
            self.history_button.config(text="Hide History ▲")
        else:
            self.history_frame.pack_forget()
            self.history_button.config(text="View History ▼")

    def populate_history(self):
        """Fills the history list frame with the user's progress."""
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()

        progress = self.controller.get_current_user_progress()
        visited_levels = progress.get("visited_levels", [])
        completed_levels = progress.get("completed_levels", [])

        if not visited_levels:
            tk.Label(self.history_list_frame, text="No levels visited yet.", bg="white", fg="grey").pack(pady=10)
            return

        for level_id in visited_levels:
            is_completed = "✓" if level_id in completed_levels else " "
            semester, level = level_id.split('/', 1)
            
            item_frame = tk.Frame(self.history_list_frame, bg="white")
            item_frame.pack(fill='x', padx=10, pady=5)
            tk.Label(item_frame, text=f"{is_completed}", font=("Helvetica", 12, "bold"), bg="white", fg="green").pack(side='left')
            label_text = f"{level}\n({semester})"
            tk.Label(item_frame, text=label_text, font=("Helvetica", 11), bg="white", justify='left').pack(side='left', padx=10)

    # --- Other methods are unchanged and correct ---
    # In client/src/ui/dashboard_screen.py in the DashboardScreen class

    def update_dashboard(self):
        """Fetches fresh data and correctly updates all dashboard components."""
        progress = self.controller.get_current_user_progress()
        all_level_ids = self.controller.get_ordered_level_ids()
        total_levels = len(all_level_ids)

        self.header_label.config(text="Dashboard")

        # --- 1. Update "Continue Where You Left Off" ---
        self.last_viewed = progress.get("last_viewed", {})
        if self.last_viewed:
            level_name = self.last_viewed.get("level", "N/A")
            screen_type = self.last_viewed.get("type", "").capitalize()
            self.last_viewed_label.config(text=f"{level_name} ({screen_type})")
            self.go_to_button.config(state='normal')
        else:
            self.last_viewed_label.config(text="No history yet. Start a level!")
            self.go_to_button.config(state='disabled')

        # --- 2. Update "Your Progress" ---
        visited = progress.get("visited_levels", [])
        completed = progress.get("completed_levels", [])
        
        # This updates the "X / Y Levels Completed" text.
        self.progress_text_label.config(text=f"{len(completed)} / {total_levels} Levels Completed")
        
        # This updates the progress bar's visual fill and percentage text.
        if total_levels > 0:
            percentage = (len(visited) / total_levels) * 100
            self.progress_bar['value'] = percentage
            self.progress_percent_label.config(text=f"{int(percentage)}%")
        else:
            self.progress_bar['value'] = 0
            self.progress_percent_label.config(text="0%")

        # --- 3. Update "What's Next" ---
        # This is the single, correct call to the find_next_level method.
        self.next_up = self.find_next_level(all_level_ids, progress)
        
        if self.next_up:
            level_name = self.next_up.get("level", "N/A")
            self.next_up_label.config(text=f">> {level_name}")
            self.start_next_button.config(state='normal')
        else:
            self.next_up_label.config(text="Congratulations! You've completed everything!")
            self.start_next_button.config(state='disabled')
    def find_next_level(self, all_level_ids, progress_data):
        """
        Finds the next logical level for the user to tackle using a
        smarter priority system.
        """
        completed_list = progress_data.get("completed_levels", [])
        visited_list = progress_data.get("visited_levels", [])
        
        # --- Priority 1: Find the level after the LAST COMPLETED one ---
        if completed_list:
            last_completed_id = completed_list[-1]
            try:
                last_index = all_level_ids.index(last_completed_id)
                if last_index + 1 < len(all_level_ids):
                    next_level_id = all_level_ids[last_index + 1]
                    semester, level = next_level_id.split('/', 1)
                    return {"semester": semester, "level": level}
            except ValueError:
                pass

        # --- Priority 2: Find the level after the LAST VISITED one ---
        if visited_list:
            last_visited_id = visited_list[-1]
            try:
                last_index = all_level_ids.index(last_visited_id)
                if last_index + 1 < len(all_level_ids):
                    next_level_id = all_level_ids[last_index + 1]
                    semester, level = next_level_id.split('/', 1)
                    return {"semester": semester, "level": level}
            except ValueError:
                pass
        
        # --- Priority 3 (Fallback): Suggest the very first level ---
        if all_level_ids:
            # Check if all levels have been completed
            # <<< FIX IS HERE: Compare list lengths directly >>>
            if len(completed_list) == len(all_level_ids):
                return None # All levels are complete

            # Otherwise, find the first level that isn't in the completed list
            for level_id in all_level_ids:
                if level_id not in completed_list:
                    semester, level = level_id.split('/', 1)
                    return {"semester": semester, "level": level}

        # --- Final Fallback: No levels exist in the curriculum ---
        return None

    def go_to_last_viewed(self):
        if self.last_viewed:
            self.controller.current_semester = self.last_viewed.get("semester"); self.controller.current_level = self.last_viewed.get("level")
            screen = "ConceptScreen" if self.last_viewed.get("type") == "concept" else "ImplementationScreen"
            self.controller.show_frame(screen)
    def start_next_level(self):
        if self.next_up:
            self.controller.current_semester = self.next_up.get("semester"); self.controller.current_level = self.next_up.get("level")
            self.controller.show_frame("ImplementationScreen")
    def confirm_and_reset_progress(self):
        is_sure = messagebox.askyesno("Confirm Reset", "Are you sure you want to permanently reset all of your learning progress?\nThis action cannot be undone.")
        if is_sure: self.controller.reset_current_user_progress(); self.update_dashboard()
    def view_full_curriculum(self): self.controller.show_frame("SemesterScreen")
    def change_mode(self): self.controller.show_frame("ModeSelectionScreen")
    def create_section_frame(self, parent, title):
        frame = tk.Frame(parent, bg="white", bd=1, relief='solid'); frame.pack(fill='x', pady=10)
        label = tk.Label(frame, text=title, font=("Helvetica", 10, "bold"), bg="white", fg="grey"); label.pack(anchor='nw', padx=10, pady=5)
        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=10)
        return frame

### Explanation of the Fixes
