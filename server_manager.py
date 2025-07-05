import tkinter as tk
import subprocess
import threading
import os
import sys
import platform
import webbrowser
from tkinter import scrolledtext, messagebox, ttk, filedialog
import json

class ServerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Local HTTP Server")
        self.root.geometry("700x580")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.bg_dark = "#282c34"
        self.bg_medium = "#3c4048"
        self.bg_light = "#4a4e56"
        self.fg_light = "#abb2bf"
        self.fg_accent = "#61afef"
        self.status_running_color = "#98c379"
        self.status_stopped_color = "#e06c75"
        self.button_normal_bg = "#5a606b"
        self.button_hover_bg = "#6e7583"
        
        self.root.configure(bg=self.bg_dark)

        self.server_process = None
        self.server_running = False

        if getattr(sys, 'frozen', False):
            self.project_path = sys._MEIPASS
        else:
            self.project_path = os.path.dirname(os.path.abspath(__file__))
            
        self.server_url = "http://127.0.0.1:5000"

        self.config_file = os.path.join(self.project_path, 'server_config.json')
        self.config = self.load_config()

        self.uploads_base_folder = self.config.get(
            'uploads_folder', 
            os.path.join(self.project_path, 'static')
        )
        self.uploads_folder = os.path.join(self.uploads_base_folder, 'uploads')

        self.database_base_folder = self.config.get(
            'database_folder', 
            self.project_path
        )
        self.database_folder = os.path.join(self.database_base_folder, 'instance')
        
        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_widgets()

        self.ensure_folder_structures()
    
    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg=self.bg_medium, padx=15, pady=10)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        tk.Label(
            header_frame, 
            text="Local HTTP Server", 
            font=("Segoe UI", 16, "bold"),
            fg=self.fg_light, 
            bg=self.bg_medium
        ).pack(side=tk.LEFT)

        control_frame = tk.Frame(self.root, bg=self.bg_dark, padx=20, pady=15)
        control_frame.grid(row=1, column=0, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)

        # Project Path
        # project_path_frame = tk.Frame(control_frame, bg=self.bg_dark)
        # project_path_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # tk.Label(
        #     project_path_frame, 
        #     text="Project Path:", 
        #     font=("Segoe UI", 9, "bold"), 
        #     fg=self.fg_light,
        #     bg=self.bg_dark
        # ).pack(side=tk.LEFT)
        
        # self.project_label = tk.Label(
        #     project_path_frame, 
        #     text=self.project_path, 
        #     font=("Consolas", 9),
        #     fg=self.fg_accent,
        #     bg=self.bg_dark,
        #     cursor="hand2"
        # )
        # self.project_label.pack(side=tk.LEFT, padx=(5,0), fill=tk.X, expand=True)
        # self.project_label.bind("<Button-1>", self.open_project_folder)

        status_control_panel = tk.Frame(control_frame, bg=self.bg_medium, padx=15, pady=15, 
                                        relief="flat", bd=1, highlightbackground=self.bg_light, highlightthickness=1)
        status_control_panel.grid(row=1, column=0, sticky="ew")
        status_control_panel.grid_columnconfigure(1, weight=1)

        tk.Label(
            status_control_panel,
            text="Server Status:",
            font=("Segoe UI", 10, "bold"),
            fg=self.fg_light,
            bg=self.bg_medium
        ).grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="w")

        self.status_label = tk.Label(
            status_control_panel,
            text="Stopped",
            font=("Segoe UI", 10, "bold"),
            fg=self.status_stopped_color,
            bg=self.bg_medium
        )
        self.status_label.grid(row=0, column=1, padx=(0, 10), pady=(0, 10), sticky="w")

        button_container = tk.Frame(status_control_panel, bg=self.bg_medium)
        button_container.grid(row=1, column=0, columnspan=2, sticky="ew")
        button_container.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_button = self.create_styled_button(
            button_container,
            text="▶ Start Server",
            bg=self.status_running_color,
            command=self.start_server
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.stop_button = self.create_styled_button(
            button_container,
            text="■ Stop Server",
            bg=self.status_stopped_color,
            command=self.stop_server,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.open_browser_button = self.create_styled_button(
            button_container,
            text="🔗 Open in Browser",
            bg=self.button_normal_bg,
            command=self.open_server_in_browser,
            state=tk.DISABLED
        )
        self.open_browser_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        uploads_frame = tk.Frame(self.root, bg=self.bg_medium, padx=15, pady=10, 
                                 relief="flat", bd=1, highlightbackground=self.bg_light, highlightthickness=1)
        uploads_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        uploads_frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            uploads_frame,
            text="Uploads Location:",
            font=("Segoe UI", 10, "bold"),
            fg=self.fg_light,
            bg=self.bg_medium
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.uploads_label = tk.Label(
            uploads_frame,
            text=self.uploads_base_folder,
            font=("Consolas", 9),
            fg=self.fg_light,
            bg=self.bg_medium,
            wraplength=500,
            justify=tk.LEFT
        )
        self.uploads_label.grid(row=0, column=1, padx=(0, 10), sticky="ew")

        button_container = tk.Frame(uploads_frame, bg=self.bg_medium)
        button_container.grid(row=0, column=2, sticky="e")

        self.change_button = self.create_styled_button(
            button_container,
            text="Change Location",
            bg=self.button_normal_bg,
            command=self.change_uploads_folder,
            width=15
        )
        self.change_button.pack(side=tk.RIGHT, padx=5)

        database_frame = tk.Frame(self.root, bg=self.bg_medium, padx=15, pady=10, 
                                 relief="flat", bd=1, highlightbackground=self.bg_light, highlightthickness=1)
        database_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        database_frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            database_frame,
            text="Database Location:",
            font=("Segoe UI", 10, "bold"),
            fg=self.fg_light,
            bg=self.bg_medium
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.database_label = tk.Label(
            database_frame,
            text=self.database_base_folder,
            font=("Consolas", 9),
            fg=self.fg_light,
            bg=self.bg_medium,
            wraplength=500,
            justify=tk.LEFT
        )
        self.database_label.grid(row=0, column=1, padx=(0, 10), sticky="ew")

        button_container = tk.Frame(database_frame, bg=self.bg_medium)
        button_container.grid(row=0, column=2, sticky="e")

        self.db_change_button = self.create_styled_button(
            button_container,
            text="Change Location",
            bg=self.button_normal_bg,
            command=self.change_database_folder,
            width=15
        )
        self.db_change_button.pack(side=tk.RIGHT, padx=5)

        separator = ttk.Separator(self.root, orient="horizontal")
        separator.grid(row=4, column=0, sticky="ew", padx=20, pady=10)

        tk.Label(
            self.root, 
            text="Server Output Log:", 
            font=("Segoe UI", 10, "bold"), 
            fg=self.fg_light,
            bg=self.bg_dark,
            anchor=tk.W
        ).grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 5))

        self.terminal_output = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#1c1c1c",
            fg=self.fg_light,
            insertbackground="white",
            padx=10,
            pady=10,
            state=tk.DISABLED,
            relief="flat",
            bd=0
        )
        self.terminal_output.grid(row=6, column=0, sticky="nsew", padx=20, pady=(0, 20))

        self.add_to_terminal("Local HTTP Server Initialized.\n")
        self.add_to_terminal("----------------------------------------\n")
        self.add_to_terminal(f"Uploads Location: {self.uploads_base_folder}\n")
        self.add_to_terminal(f"Database Location: {self.database_base_folder}\n")
        self.add_to_terminal("1. Click 'Start Server' to launch the Flask server.\n")
        self.add_to_terminal("2. Use 'Stop Server' to terminate.\n")
        self.add_to_terminal("3. Debug mode is turned OFF for production-like use.\n")
        self.add_to_terminal("----------------------------------------\n")
        self.add_to_terminal("Ready to start server...\n")

    def create_styled_button(self, parent, text, bg, command, state=tk.NORMAL, width=None):
        button = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            fg="white",
            padx=15,
            pady=8,
            command=command,
            state=state,
            relief="flat",
            activebackground=bg,
            activeforeground="white",
            borderwidth=0,
            highlightthickness=0,
            width=width
        )
        button.bind("<Enter>", lambda e: button.config(bg=self.button_hover_bg) if button["state"] == tk.NORMAL else None)
        button.bind("<Leave>", lambda e: button.config(bg=bg) if button["state"] == tk.NORMAL else None)
        return button

    def load_config(self):
        """Load configuration from file or return default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.add_to_terminal(f"Error loading config: {str(e)}\n")
                return {}
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
            return True
        except Exception as e:
            self.add_to_terminal(f"Error saving config: {str(e)}\n")
            return False
            
    def change_uploads_folder(self):
        """Open dialog to select new uploads base location"""
        new_base = filedialog.askdirectory(
            title="Select Uploads Base Location",
            initialdir=self.uploads_base_folder
        )
        
        if new_base:
            self.uploads_base_folder = new_base
            self.uploads_folder = os.path.join(new_base, 'uploads')
            self.uploads_label.config(text=self.uploads_base_folder)
            self.config['uploads_folder'] = self.uploads_base_folder
            self.save_config()
            self.add_to_terminal(f"Uploads location changed to: {self.uploads_base_folder}\n")
            self.ensure_folder_structures()
    
    def change_database_folder(self):
        """Open dialog to select new database base location"""
        new_base = filedialog.askdirectory(
            title="Select Database Base Location",
            initialdir=self.database_base_folder
        )
        
        if new_base:
            self.database_base_folder = new_base
            self.database_folder = os.path.join(new_base, 'instance')
            self.database_label.config(text=self.database_base_folder)
            self.config['database_folder'] = self.database_base_folder
            self.save_config()
            self.add_to_terminal(f"Database location changed to: {self.database_base_folder}\n")
            self.ensure_folder_structures()
    
    def ensure_folder_structures(self):
        """Ensure required folder structures exist for both uploads and database"""

        required_uploads_folders = ['images', 'pdfs', 'videos']
        created_any_uploads = False
        
        try:
            if not os.path.exists(self.uploads_folder):
                os.makedirs(self.uploads_folder)
                self.add_to_terminal(f"Created uploads folder: {self.uploads_folder}\n")
                created_any_uploads = True
            
            for folder in required_uploads_folders:
                folder_path = os.path.join(self.uploads_folder, folder)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    self.add_to_terminal(f"Created folder: {folder_path}\n")
                    created_any_uploads = True
            
            if not created_any_uploads:
                self.add_to_terminal("All required upload folders already exist\n")
            else:
                self.add_to_terminal("Created missing upload folder structure\n")
        except Exception as e:
            self.add_to_terminal(f"Error creating upload structure: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to create upload structure: {e}")

        created_db_folder = False
        try:
            if not os.path.exists(self.database_folder):
                os.makedirs(self.database_folder)
                self.add_to_terminal(f"Created database folder: {self.database_folder}\n")
                created_db_folder = True
            else:
                self.add_to_terminal(f"Database folder exists: {self.database_folder}\n")

            db_file = os.path.join(self.database_folder, 'articles.db')
            if not os.path.exists(db_file):
                self.add_to_terminal("Database file does not exist - will be created on first run\n")
            else:
                self.add_to_terminal(f"Database file exists: {db_file}\n")
        except Exception as e:
            self.add_to_terminal(f"Error creating database structure: {str(e)}\n")
            messagebox.showerror("Error", f"Failed to create database structure: {e}")

    def start_server(self):
        if not self.server_running:
            self.server_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.open_browser_button.config(state=tk.NORMAL)
            self.status_label.config(text="Starting...", fg=self.fg_accent)
            
            self.add_to_terminal("Starting Flask server...\n")
            self.add_to_terminal("----------------------------------------\n")
            self.add_to_terminal(f"Using uploads folder: {self.uploads_folder}\n")
            self.add_to_terminal(f"Using database folder: {self.database_folder}\n")

            self.add_to_terminal("Note: Debug mode is turned OFF\n")
            server_thread = threading.Thread(target=self.run_server, daemon=True)
            server_thread.start()
    
    def run_server(self):
        try:
            if getattr(sys, 'frozen', False):
                python_executable = sys.executable 
                app_script_path = os.path.join(sys._MEIPASS, "app.py")
                run_cwd = sys._MEIPASS 
            else:
                python_executable = sys.executable
                app_script_path = os.path.join(self.project_path, "app.py")
                run_cwd = self.project_path

            env = os.environ.copy()
            env['UPLOAD_FOLDER'] = self.uploads_folder
            env['DATABASE_FOLDER'] = self.database_folder
            
            self.server_process = subprocess.Popen(
                [python_executable, app_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=run_cwd,
                env=env
            )

            self.root.after(0, lambda: self.status_label.config(text="Running", fg=self.status_running_color))

            for line in self.server_process.stdout:
                self.add_to_terminal(line)
                
            self.server_process.stdout.close()
            return_code = self.server_process.wait()
            
            if return_code:
                self.add_to_terminal(f"\nServer exited with code {return_code}\n")
            else:
                 self.add_to_terminal("\nServer process terminated gracefully.\n")
                
        except FileNotFoundError:
            self.add_to_terminal(f"ERROR: Could not find '{app_script_path}'.\n")
            messagebox.showerror("Error", f"Server script 'app.py' not found at {app_script_path}.")
        except Exception as e:
            self.add_to_terminal(f"ERROR: An unexpected error occurred: {str(e)}\n")
            messagebox.showerror("Error", f"An error occurred while starting the server: {e}")
            
        self.server_running = False
        self.root.after(0, self.reset_buttons)
        
    def reset_buttons(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.open_browser_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", fg=self.status_stopped_color)
        self.add_to_terminal("\nServer stopped.\n")
    
    def stop_server(self):
        if self.server_running and self.server_process:
            self.add_to_terminal("\nStopping server...\n")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                self.add_to_terminal("Server terminated gracefully.\n")
            except subprocess.TimeoutExpired:
                self.add_to_terminal("Server did not terminate, forcing kill...\n")
                self.server_process.kill()
                self.server_process.wait()
                self.add_to_terminal("Server force-killed.\n")
            except Exception as e:
                self.add_to_terminal(f"Error during server stop: {e}\n")

        self.server_running = False
        self.root.after(0, self.reset_buttons)

    def add_to_terminal(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
    
    def open_server_in_browser(self):
        if self.server_running:
            try:
                webbrowser.open_new_tab(self.server_url)
                self.add_to_terminal(f"Opened {self.server_url} in browser.\n")
            except Exception as e:
                self.add_to_terminal(f"ERROR: Could not open browser: {e}\n")
                messagebox.showerror("Error", f"Failed to open browser: {e}")
        else:
            messagebox.showinfo("Server Not Running", "The server is not currently running to open in a browser.")

    def open_project_folder(self, event=None):
        try:
            if platform.system() == "Windows":
                os.startfile(self.project_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.project_path])
            else:
                subprocess.Popen(["xdg-open", self.project_path])
            self.add_to_terminal(f"Opened project folder: {self.project_path}\n")
        except Exception as e:
            self.add_to_terminal(f"ERROR: Could not open project folder: {e}\n")
            messagebox.showerror("Error", f"Failed to open project folder: {e}")

    def on_close(self):
        if self.server_running:
            if messagebox.askokcancel("Quit Application", "Server is still running. Do you want to stop it and quit?"):
                self.stop_server()
                self.root.after(500, self.root.destroy) 
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerManager(root)
    root.mainloop()