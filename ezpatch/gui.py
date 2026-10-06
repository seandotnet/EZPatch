import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
import os

from .config import APP_NAME, APP_VERSION, DEFAULT_REPLAY_DIR
from .utils import setup_logging, get_latest_replay, get_resource_path
from .patcher import ReplayPatcher, VersionInfo

class EZPatchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # setup the main window 
        self.title(f"{APP_NAME} v{APP_VERSION} - by git/seandotnet")
        self.geometry("800x700")
        self.resizable(True, True)
        
        # set theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # set the window icon 
        icon_path = get_resource_path("ezpatch/assets/EZlogo.ico")
        if icon_path.exists():
            self.iconbitmap(str(icon_path))
            
        # variables
        self.working_replay_path = ctk.StringVar()
        self.broken_replay_path = ctk.StringVar()
        self.broken_folder_path = ctk.StringVar()
        
        # settings
        self.log_level = ctk.StringVar(value="Info")
        self.keep_originals = ctk.BooleanVar(value=True)
        self.overwrite_patched = ctk.BooleanVar(value=False)
        self.move_to_backups = ctk.BooleanVar(value=True)
        self.skip_old_seasons = ctk.BooleanVar(value=False)
        
        # stats
        self.patched_count = 0
        self.skipped_count = 0
        
        # init logger and patcher
        self.logger = setup_logging(self.log_level.get())
        self.patcher = ReplayPatcher(self.logger)
        
        self.create_widgets()
        
    def create_widgets(self):
        # create the tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_main = self.tabview.add("Main")
        self.tab_settings = self.tabview.add("Settings")
        
        self.create_main_tab()
        self.create_settings_tab()
        
    def create_main_tab(self):
        # working replay section
        working_ame = ctk.CTkame(self.tab_main)
        working_ame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(working_ame, text="Working Replay File:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        working_input_ame = ctk.CTkame(working_ame, fg_color="transparent")
        working_input_ame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkEntry(working_input_ame, textvariable=self.working_replay_path, width=500).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(working_input_ame, text="Browse", command=self.browse_working_replay, width=100).pack(side="left")
        
        # broken replays section
        broken_ame = ctk.CTkame(self.tab_main)
        broken_ame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(broken_ame, text="Broken Replay(s):", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        # single file
        single_input_ame = ctk.CTkame(broken_ame, fg_color="transparent")
        single_input_ame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(single_input_ame, text="Single File:").pack(side="left", padx=(0, 10))
        ctk.CTkEntry(single_input_ame, textvariable=self.broken_replay_path, width=400).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(single_input_ame, text="Browse File", command=self.browse_broken_replay, width=100).pack(side="left")
        
        # folder
        folder_input_ame = ctk.CTkame(broken_ame, fg_color="transparent")
        folder_input_ame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(folder_input_ame, text="Folder:      ").pack(side="left", padx=(0, 10))
        ctk.CTkEntry(folder_input_ame, textvariable=self.broken_folder_path, width=400).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(folder_input_ame, text="Browse Folder", command=self.browse_broken_folder, width=100).pack(side="left")
        
        # action buttons
        button_ame = ctk.CTkame(self.tab_main, fg_color="transparent")
        button_ame.pack(fill="x", padx=10, pady=10)
        
        self.patch_button = ctk.CTkButton(button_ame, text="Patch Replays", command=self.start_patching, fg_color="green", hover_color="darkgreen")
        self.patch_button.pack(side="left", padx=5)
        
        self.auto_button = ctk.CTkButton(button_ame, text="Auto Patch (Latest)", command=self.auto_patch)
        self.auto_button.pack(side="left", padx=5)
        
        # progress and output
        self.progress = ctk.CTkProgressBar(self.tab_main, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=10)
        self.progress.set(0)
        
        self.summary_label = ctk.CTkLabel(self.tab_main, text="Ready to patch replays...")
        self.summary_label.pack(anchor="w", padx=10)
        
        self.output_text = ctk.CTkTextbox(self.tab_main, height=200, state="disabled")
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_settings_tab(self):
        # log level
        log_ame = ctk.CTkame(self.tab_settings)
        log_ame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(log_ame, text="Log Level", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        ctk.CTkRadioButton(log_ame, text="Info (default)", variable=self.log_level, value="Info", command=self.update_logger).pack(anchor="w", padx=10, pady=5)
        ctk.CTkRadioButton(log_ame, text="Debug (sean)", variable=self.log_level, value="Debug", command=self.update_logger).pack(anchor="w", padx=10, pady=5)
        
        # options
        options_ame = ctk.CTkame(self.tab_settings)
        options_ame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(options_ame, text="Options", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        
        ctk.CTkCheckBox(options_ame, text="Keep original files for backups", variable=self.keep_originals, command=self.on_keep_originals_change).pack(anchor="w", padx=10, pady=5)
        ctk.CTkCheckBox(options_ame, text="Overwrite previously patched replays", variable=self.overwrite_patched).pack(anchor="w", padx=10, pady=5)
        ctk.CTkCheckBox(options_ame, text="Move backups to ./Backups directory", variable=self.move_to_backups).pack(anchor="w", padx=10, pady=5)
        ctk.CTkCheckBox(options_ame, text="Skip replay files from previous seasons", variable=self.skip_old_seasons).pack(anchor="w", padx=10, pady=5)
        
    def update_logger(self):
        self.logger = setup_logging(self.log_level.get())
        self.patcher.logger = self.logger
        
    def on_keep_originals_change(self):
        if not self.keep_originals.get():
            result = messagebox.askyesno("Warning", "This will delete original files after patching! Are you sure ?")
            if not result:
                self.keep_originals.set(True)
                
    def browse_working_replay(self):
        initial_dir = DEFAULT_REPLAY_DIR if DEFAULT_REPLAY_DIR.exists() else "."
        filename = filedialog.askopenfilename(
            title="Select Working Replay File",
            defaultextension=".replay",
            filetypes=[("Replay files", "*.replay"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        if filename:
            self.working_replay_path.set(filename)
            
    def browse_broken_replay(self):
        initial_dir = DEFAULT_REPLAY_DIR if DEFAULT_REPLAY_DIR.exists() else "."
        filename = filedialog.askopenfilename(
            title="Select Broken Replay File",
            defaultextension=".replay",
            filetypes=[("Replay files", "*.replay"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        if filename:
            self.broken_replay_path.set(filename)
            
    def browse_broken_folder(self):
        initial_dir = DEFAULT_REPLAY_DIR if DEFAULT_REPLAY_DIR.exists() else "."
        folder = filedialog.askdirectory(
            title="Select Broken Replays Folder",
            initialdir=initial_dir
        )
        if folder:
            self.broken_folder_path.set(folder)
            
    def auto_patch(self):
        result = messagebox.askyesno("Auto Patch", "Continue with auto patch? This will automatically find the latest replay and patch all replays in the default folder.")
        if not result:
            return
            
        if DEFAULT_REPLAY_DIR.exists():
            latest_file = get_latest_replay(DEFAULT_REPLAY_DIR)
            if latest_file:
                self.working_replay_path.set(str(latest_file))
                self.broken_folder_path.set(str(DEFAULT_REPLAY_DIR))
                self.start_patching()
            else:
                messagebox.showerror("Error", "No replay files found in default directory !")
        else:
            messagebox.showerror("Error", "Default Fortnite replay directory not found!")
            
    def log_to_ui(self, message: str, level: str = "INFO"):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"{level}: {message}\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")
        
    def start_patching(self):
        if not self.keep_originals.get():
            result = messagebox.askyesno("Final Warning", "You have chosen to delete original files! This cannot be undone. Continue?")
            if not result:
                return
                
        # disable buttons
        self.patch_button.configure(state="disabled")
        self.auto_button.configure(state="disabled")
        self.progress.start()
        
        # clear output
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        
        # run in thread so ui doesnt eeze lol
        thread = threading.Thread(target=self._patch_thread)
        thread.daemon = True
        thread.start()
        
    def _patch_thread(self):
        try:
            self.patched_count = 0
            self.skipped_count = 0
            
            working_file = self.working_replay_path.get()
            if not working_file or not os.path.exists(working_file):
                self.log_to_ui("Working replay file not selected or doesn't exist!", "ERROR")
                self.logger.error("working file missing")
                return
                
            working_path = Path(working_file)
            
            # extract version
            version_info = self.patcher.extract_version(working_path)
            if not version_info:
                self.log_to_ui("Failed to extract version info from working file", "ERROR")
                return
                
            self.log_to_ui(f"Extracted version info - Version: {version_info.version_bytes.hex()}")
            self.logger.info(f"extracted version info - version: {version_info.version_bytes.hex()}")
            
            files_to_process = []
            
            # single file
            broken_file = self.broken_replay_path.get()
            if broken_file and os.path.exists(broken_file):
                files_to_process.append(Path(broken_file))
                
            # folder
            broken_folder = self.broken_folder_path.get()
            if broken_folder and os.path.exists(broken_folder):
                folder_path = Path(broken_folder)
                for f in folder_path.glob("*.replay"):
                    if f != working_path: # dont patch the working file lol
                        files_to_process.append(f)
                        
            if not files_to_process:
                self.log_to_ui("No replay files to process!", "ERROR")
                return
                
            # remove duplicates
            files_to_process = list(set(files_to_process))
            
            for file_path in files_to_process:
                self.log_to_ui(f"Processing: {file_path.name}")
                result = self.patcher.process_file(
                    broken_path=file_path,
                    version_info=version_info,
                    keep_originals=self.keep_originals.get(),
                    move_to_backups=self.move_to_backups.get(),
                    overwrite_patched=self.overwrite_patched.get(),
                    skip_old_seasons=self.skip_old_seasons.get()
                )
                
                if result.success:
                    self.patched_count += 1
                    self.log_to_ui(f"Patched: {file_path.name}")
                    self.logger.info(f"patched: {file_path.name}")
                else:
                    self.skipped_count += 1
                    self.log_to_ui(f"Skipped {file_path.name}: {result.message}")
                    self.logger.info(f"skipped {file_path.name}: {result.message}")
                    
            summary = f"Completed: {self.patched_count} Replays Patched | {self.skipped_count} Skipped"
            self.log_to_ui(summary)
            self.logger.info(summary)
            
            # update summary label in main thread
            self.after(0, lambda: self.summary_label.configure(text=summary))
            
        except Exception as e:
            self.log_to_ui(f"Unexpected error: {e}", "ERROR")
            self.logger.error(f"unexpected error: {e}")
        finally:
            # re-enable buttons
            self.after(0, self._enable_buttons)
            
    def _enable_buttons(self):
        self.patch_button.configure(state="normal")
        self.auto_button.configure(state="normal")
        self.progress.stop()
