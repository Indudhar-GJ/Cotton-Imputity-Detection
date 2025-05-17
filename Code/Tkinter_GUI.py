import tkinter as tk
from tkinter import messagebox, filedialog, ttk, Toplevel
import subprocess
import threading
import time
import os
import shutil
from PIL import Image, ImageTk
import json
from roboflow import Roboflow
import requests
from datetime import datetime
from pathlib import Path  # Add this at the top with other imports
import threading
import time
import shutil
from pathlib import Path
import requests
from urllib.parse import urlparse
import requests
import time
import sqlite3
from tkinter import messagebox  # For showing messages to the user
import sqlite3
from pathlib import Path
from datetime import datetime
import shlex


def initialize_settings(conn):
    """Create a new record with initial values"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO params (
                AcquisitionLineRateEnable, ReverseX, GammaEnable,
                CreatedAt, LastModified
            ) VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (False, False, True))  # Default initial values
        conn.commit()
        return cursor.lastrowid  # Return the ID of the new record
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def update_settings(conn, settings_id, **kwargs):
    """Update specific fields of an existing record"""
    if not kwargs:
        return
        
    set_clause = ", ".join([f"{key} = ?" for key in kwargs])
    values = list(kwargs.values())
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE params
            SET {set_clause}, LastModified = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values + [settings_id])
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

conn = sqlite3.connect('config.db')
temp=initialize_settings(conn)
# 1. At program start - insert initial values
settings_id = 1
print(f"Created new settings record with ID: {settings_id}")

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tile Inspection System")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # Camera parameters
        self.camera_params = {
            # Boolean parameters
            "AcquisitionLineRateEnable": True,
            "ReverseX": False,
            "GammaEnable": True,
            "HueEnable": False,
            "SaturationEnable": True,
            
            # Hex parameter
            "PixelFormat": 0x01080009,  # Example hex value
            
            # Integer parameters
            "Exposure": 5000,
            "AcquisitionLineRate": 10000,
            "AutoExposureTimeLowerLimit": 100,
            "AutoExposureTimeUpperLimit": 10000,
            "Width": 1920,
            "Height": 1080,
            "BalanceWhiteAuto": 1
        }
        
        # Create main container
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize UI
        self.create_widgets()
        self.create_menu()
        
    def create_menu(self):
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Install Dependencies", command=self.install_dependencies)
        tools_menu.add_command(label="Configure Camera", command=self.configure_camera)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
    
    def create_widgets(self):
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Tile Inspection System", 
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Buttons
        ttk.Button(
            buttons_frame, 
            text="Install Dependencies", 
            command=self.install_dependencies,
            width=25
        ).pack(pady=10, fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="Upload Model File", 
            command=self.upload_model,
            width=25
        ).pack(pady=10, fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="Configure Camera", 
            command=self.configure_camera,
            width=25
        ).pack(pady=10, fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="Run Inspection Script", 
            command=self.run_script,
            width=25
        ).pack(pady=10, fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="View images With no Impurity", 
            command=self.show_images,
            width=25
        ).pack(pady=10, fill=tk.X)

        # Add this with your other buttons
        ttk.Button(
            buttons_frame, 
            text="Upload to Roboflow", 
            command=self.upload_to_roboflow,
            width=25
        ).pack(pady=10, fill=tk.X)

        ttk.Button(
            buttons_frame,
            text="Download Dataset",
            command=self._show_roboflow_download_dialog,
            style="Accent.TButton"
        ).pack(pady=10, fill=tk.X)

        ttk.Button(
            buttons_frame,
            text="Train Model",
            command=self._prepare_training,
            style="Accent.TButton"
        ).pack(pady=10, fill=tk.X)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
    
    def install_dependencies(self):
        self.status_var.set("Installing dependencies...")
        self.update()  # Force UI update
        
        # Path to your commands file (create this file with all installation commands)
        commands_file = "install_commands.txt"
        
        if not os.path.exists(commands_file):
            messagebox.showerror("Error", f"Commands file not found: {commands_file}")
            self.status_var.set("Missing commands file")
            return

        try:
            with open(commands_file, 'r') as f:
                commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            for cmd in commands:
                self.status_var.set(f"Running: {cmd[:]}...")  # Show first 50 chars
                self.update()
                
                try:
                    # Run each command in the system shell
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Log successful output
                    if result.stdout:
                        print(f"Output for '{cmd}':\n{result.stdout}")
                        
                except subprocess.CalledProcessError as e:
                    error_msg = f"Failed to execute: {cmd}\nError: {e.stderr if e.stderr else str(e)}"
                    print(error_msg)
                    messagebox.showerror("Installation Error", error_msg)
                    self.status_var.set("Installation failed")
                    return
            
            messagebox.showinfo("Success", "All dependencies installed successfully!")
            self.status_var.set("Dependencies installed")
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Installation error")
            print(error_msg)
    
    def upload_model(self):
        file_path = filedialog.askopenfilename(
            title="Select a Model File",
            filetypes=[
                ("Model Files", "*.pt *.engine"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE params 
                SET ModelPath = ? 
                WHERE id = ?
            """, (file_path, settings_id))
            conn.commit()
            print(f"Updated Model Path")
            try:
                # Here you would add code to actually handle the model file
                messagebox.showinfo("Success", f"Model file loaded successfully!\n{file_path}")
                self.status_var.set(f"Model loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model: {str(e)}")
                self.status_var.set("Model loading failed")
    
    def configure_camera(self):
        config_window = Toplevel(self)
        config_window.title("Camera Configuration")
        config_window.geometry("600x700")
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(config_window)
        scrollbar = ttk.Scrollbar(config_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Define parameter types
        bool_params = ["AcquisitionLineRateEnable", "ReverseX", "GammaEnable", 
                    "HueEnable", "SaturationEnable"]
        hex_params = ["PixelFormat"]
        int_params = ["Exposure", "AcquisitionLineRate", "AutoExposureTimeLowerLimit",
                    "AutoExposureTimeUpperLimit", "Width", "Height", "BalanceWhiteAuto"]
        
        self.entry_vars = {}  # To store all entry variables
        
        row = 0
        
        # Create controls for each parameter type
        def create_control(param, value, param_type):
            nonlocal row
            ttk.Label(scrollable_frame, text=param).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            
            if param_type == "bool":
                var = tk.BooleanVar(value=bool(value))
                cb = ttk.Checkbutton(scrollable_frame, variable=var, text="Enable")
                cb.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                self.entry_vars[param] = var
            elif param_type == "hex":
                var = tk.StringVar(value=f"0x{value:02X}")
                entry = ttk.Entry(scrollable_frame, textvariable=var, width=10)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                self.entry_vars[param] = var
            else:  # int
                var = tk.IntVar(value=value)
                entry = ttk.Entry(scrollable_frame, textvariable=var, width=10)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                self.entry_vars[param] = var
            
            row += 1
        
        # Add boolean parameters
        ttk.Label(scrollable_frame, text="Boolean Parameters", font=("Helvetica", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", pady=10)
        row += 1
        for param in bool_params:
            create_control(param, self.camera_params.get(param, False), "bool")
        
        # Add hex parameters
        ttk.Label(scrollable_frame, text="Hex Parameters", font=("Helvetica", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", pady=10)
        row += 1
        for param in hex_params:
            create_control(param, self.camera_params.get(param, 0), "hex")
        
        # Add integer parameters
        ttk.Label(scrollable_frame, text="Integer Parameters", font=("Helvetica", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", pady=10)
        row += 1
        for param in int_params:
            create_control(param, self.camera_params.get(param, 0), "int")
        
        # Save button
        ttk.Button(
            scrollable_frame,
            text="Save Parameters",
            command=lambda: self.save_camera_params(config_window)
        ).grid(row=row, column=0, columnspan=2, pady=20)

    def save_camera_params(self, window):
        try:
            for param, var in self.entry_vars.items():
                if param in ["AcquisitionLineRateEnable", "ReverseX", "GammaEnable", 
                            "HueEnable", "SaturationEnable"]:
                    self.camera_params[param] = var.get()
                elif param == "PixelFormat":
                    # Convert hex string to integer
                    hex_str = var.get().strip()
                    if hex_str.startswith("0x"):
                        self.camera_params[param] = int(hex_str, 16)
                    else:
                        self.camera_params[param] = int(hex_str)
                else:
                    self.camera_params[param] = var.get()
            
            cursor=conn.cursor()
            cursor.execute("""
                UPDATE params SET
                    AcquisitionLineRateEnable = ?,
                    ReverseX = ?,
                    GammaEnable = ?,
                    HueEnable = ?,
                    SaturationEnable = ?,
                    PixelFormat = ?,
                    Exposure = ?,
                    AcquisitionLineRate = ?,
                    AutoExposureTimeLowerLimit = ?,
                    AutoExposureTimeUpperLimit = ?,
                    Width = ?,
                    Height = ?,
                    BalanceWhiteAuto = ?,
                    LastModified = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                self.camera_params.get("AcquisitionLineRateEnable", False),
                self.camera_params.get("ReverseX", False),
                self.camera_params.get("GammaEnable", True),
                self.camera_params.get("HueEnable", False),
                self.camera_params.get("SaturationEnable", True),
                self.camera_params.get("PixelFormat", 0),
                self.camera_params.get("Exposure", 0),
                self.camera_params.get("AcquisitionLineRate", 0),
                self.camera_params.get("AutoExposureTimeLowerLimit", 0),
                self.camera_params.get("AutoExposureTimeUpperLimit", 0),
                self.camera_params.get("Width", 0),
                self.camera_params.get("Height", 0),
                self.camera_params.get("BalanceWhiteAuto", 0),
                settings_id
            ))
            
            conn.commit()
            
            
            messagebox.showinfo("Success", "Camera parameters updated!")
            window.destroy()
            self.status_var.set("Camera configuration saved")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid parameter value: {str(e)}")
    
    def run_script(self):
        # First save the current configuration
        self.save_config()
        
        script_path = filedialog.askopenfilename(
            title="Select Inspection Script",
            filetypes=[("Python Files", "*.py")]
        )
        if not script_path:
            return
        
        self.status_var.set("Running inspection script...")
        
        def execute_script():
            try:
                # Save configuration again right before execution
                self.save_config()
                
                process = subprocess.Popen(["python", script_path])
                time.sleep(10)  # Run for 10 seconds (adjustable)
                process.terminate()
                self.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    "Script execution stopped after 10 seconds!"
                ))
                self.after(0, self.show_images)
                self.after(0, lambda: self.status_var.set("Inspection complete"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Error", 
                    f"Script execution failed: {str(e)}"
                ))
                self.after(0, lambda: self.status_var.set("Inspection failed"))
        
        threading.Thread(target=execute_script, daemon=True).start()

    def save_config(self):
        """Save current configuration to file"""
        config = {
            "camera_params": self.camera_params,
            "model_path": getattr(self, 'current_model_path', None)
        }
        
        try:
            with open("inspection_config.json", "w") as f:
                json.dump(config, f, indent=4)
            self.status_var.set("Configuration saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
            self.status_var.set("Config save failed")

    # def upload_model(self):
    #     file_path = filedialog.askopenfilename(
    #         title="Select a Model File",
    #         filetypes=[
    #             ("Model Files", "*.pt *.engine"),
    #             ("All Files", "*.*")
    #         ]
    #     )
    #     if file_path:
    #         try:
    #             self.current_model_path = file_path
    #             messagebox.showinfo("Success", f"Model file loaded successfully!\n{file_path}")
    #             self.status_var.set(f"Model loaded: {os.path.basename(file_path)}")
    #             self.save_config()  # Save after uploading model
    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to load model: {str(e)}")
    #             self.status_var.set("Model loading failed")
    
    def show_images(self):
        image_window = Toplevel(self)
        image_window.title("Inspection Results")
        image_window.geometry("800x600")
        
        # Create main container
        main_frame = ttk.Frame(image_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Mouse wheel binding
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cleanup on window close
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
            image_window.destroy()
        
        image_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Image display with clickable rows and tick marks
        clear_tiles_folder = "clear_tiles"
        new_impurities_folder = "new_impurities"
        os.makedirs(new_impurities_folder, exist_ok=True)
        
        images = [f for f in os.listdir(clear_tiles_folder) 
                if f.lower().endswith(('png', 'jpg', 'jpeg'))]
        self.selected_images = []
        self.selection_states = {}  # To track selection states
        
        # Create a custom style for selected rows
        style = ttk.Style()
        style.configure("Selected.TFrame", background="#e6f3ff")
        
        # Display each image with selection
        for img in images:
            img_path = os.path.join(clear_tiles_folder, img)
            
            try:
                # Load and resize image
                image = Image.open(img_path)
                image.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(image)
                
                # Create frame for each image
                frame = ttk.Frame(scrollable_frame, padding=5)
                frame.pack(fill=tk.X, pady=2)
                
                # Store references
                frame.photo = photo
                frame.img_name = img
                self.selection_states[img] = False
                
                # Selection indicator (initially empty)
                selection_label = ttk.Label(frame, text="", width=3, font=("Arial", 12))
                selection_label.pack(side="left", padx=5)
                
                # Image label
                img_label = ttk.Label(frame, image=photo)
                img_label.image = photo
                img_label.pack(side="left")
                
                # Filename label
                ttk.Label(frame, text=img).pack(side="left", padx=10)
                
                # Function to toggle selection
                def toggle_selection(img_name=img, frame=frame, label=selection_label):
                    self.selection_states[img_name] = not self.selection_states[img_name]
                    
                    if self.selection_states[img_name]:
                        label.config(text="✓", foreground="green")
                        frame.configure(style="Selected.TFrame")
                        if img_name not in self.selected_images:
                            self.selected_images.append(img_name)
                    else:
                        label.config(text="")
                        frame.configure(style="TFrame")
                        if img_name in self.selected_images:
                            self.selected_images.remove(img_name)
                
                # Bind click events to the entire row
                for widget in [frame, selection_label, img_label]:
                    widget.bind("<Button-1>", lambda e, t=toggle_selection: t())
                
            except Exception as e:
                print(f"Error loading image {img}: {str(e)}")
        
        # Action buttons
        button_frame = ttk.Frame(image_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Move Selected to Impurities",
            command=lambda: self.move_selected_images_with_close(
                clear_tiles_folder,
                new_impurities_folder,
                image_window  # Pass the window reference
            )
        ).pack(side="left", padx=10)
        
        ttk.Button(
            button_frame,
            text="Close",
            command=on_close
        ).pack(side="right", padx=10)
    
    def toggle_image_selection(self, var, image_name):
        if var.get():
            self.selected_images.append(image_name)
        else:
            self.selected_images.remove(image_name)
    
    def move_selected_images(self, source_folder, dest_folder):
        if not self.selected_images:
            messagebox.showwarning("Warning", "No images selected!", parent=self)  # Show in main window
            return
        
        try:
            for img in self.selected_images:
                src = os.path.join(source_folder, img)
                dst = os.path.join(dest_folder, img)
                shutil.move(src, dst)
            
            # Show success message in the current window and close it
            response = messagebox.showinfo(
                "Success", 
                f"Moved {len(self.selected_images)} images!",
                parent=self.focus_get()  # Show in the current active window
            )
            
            # Close the image viewing window after OK is clicked
            if response == "ok":
                for window in self.winfo_children():
                    if isinstance(window, tk.Toplevel) and window.title() == "Inspection Results":
                        window.destroy()
                        break
            
            self.selected_images = []  # Clear selection
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move images: {str(e)}", parent=self.focus_get())
    
    def move_selected_images_with_close(self, source_folder, dest_folder, window_to_close):
        self.move_selected_images(source_folder, dest_folder)
        window_to_close.destroy()
    
    def upload_to_roboflow(self):
        try:
            from roboflow import Roboflow
        except ImportError:
            messagebox.showerror("Error", "Roboflow package not installed.\nRun: pip install roboflow", parent=self)
            return

        # Create license selection window
        license_window = Toplevel(self)
        license_window.title("Project License")
        license_window.geometry("400x250")
        
        # License options
        ttk.Label(license_window, text="Select Project License:").pack(pady=10)
        
        license_var = tk.StringVar(value="mit")
        licenses = {
            "MIT": "MIT",
            "Apache 2.0": "apache-2.0", 
            "GPL 3.0": "gpl-3.0",
            "CC BY 4.0": "cc-by-4.0",
            "Private (Non-Commercial)": "private-nc"
        }
        
        for display_name, license_val in licenses.items():
            ttk.Radiobutton(
                license_window,
                text=display_name,
                variable=license_var,
                value=license_val
            ).pack(anchor="w", padx=20)
        
        def on_license_selected():
            self.roboflow_license = license_var.get()
            license_window.destroy()
            self._show_roboflow_upload_dialog()
        
        ttk.Button(
            license_window,
            text="Continue",
            command=on_license_selected
        ).pack(pady=15)

    def _show_roboflow_upload_dialog(self):
        upload_window = Toplevel(self)
        upload_window.title("Create New Roboflow Project")
        upload_window.geometry("500x300")
        
        # Hardcoded API key (replace with your actual key)
        self.API_KEY = "BAV3BZKUATBxapsB90L4"  # Store as instance variable
        
        # Try to fetch workspace name automatically
        self.workspace_name = None
        try:
            response = requests.get(f"https://api.roboflow.com/?api_key={self.API_KEY}")
            if response.status_code == 200:
                self.workspace_name = response.json().get("workspace")
        except Exception as e:
            print(f"Could not fetch workspace: {str(e)}")
        
        # Only need project name entry now
        ttk.Label(upload_window, text="New Project Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.project_name_entry = ttk.Entry(upload_window, width=40)
        self.project_name_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # Show workspace info
        if self.workspace_name:
            ttk.Label(upload_window, 
                    text=f"Workspace: {self.workspace_name}",
                    foreground="green").grid(row=1, column=0, columnspan=2, pady=5)
        else:
            ttk.Label(upload_window,
                    text="Could not fetch workspace automatically",
                    foreground="red").grid(row=1, column=0, columnspan=2, pady=5)
        
        # Project type dropdown
        ttk.Label(upload_window, text="Project Type:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.project_type_var = tk.StringVar(value="object-detection")
        ttk.Combobox(upload_window,
                    textvariable=self.project_type_var,
                    values=["object-detection", "instance-segmentation", "classification"],
                    state="readonly").grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(upload_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        upload_btn = ttk.Button(
            button_frame,
            text="Create Project & Upload",
            command=self._perform_roboflow_upload,
            style="Accent.TButton"
        )
        upload_btn.pack(side=tk.RIGHT, padx=5)
        
        if not self.workspace_name:
            upload_btn.state(["disabled"])
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=upload_window.destroy
        ).pack(side=tk.RIGHT)

    def _perform_roboflow_upload(self):
        try:
            # Get project name from entry widget
            project_name = self.project_name_entry.get().strip().replace(" ", "-")
            project_type = self.project_type_var.get()
            
            if not project_name:
                messagebox.showerror("Error", "Project name is required!", parent=self)
                return
                
            # Initialize Roboflow with hardcoded API key
            rf = Roboflow(api_key=self.API_KEY)
            workspace = rf.workspace(self.workspace_name)
            
            # Create or get existing project
            try:
                project = workspace.create_project(
                    project_name=project_name,
                    project_type=project_type,
                    project_license=self.roboflow_license,
                    annotation=f"cotseed-{project_type}"
                )
                project_created = True
            except Exception as e:
                if "already exists" in str(e):
                    project = workspace.project(project_name)
                    project_created = False
                else:
                    raise e

            # Upload images from new_impurities folder
            folder_path = "new_impurities"
            image_files = [f for f in os.listdir(folder_path) 
                        if f.lower().endswith(('png', 'jpg', 'jpeg', '.bmp'))]
            
            success_count = 0
            for i, img in enumerate(image_files, 1):
                img_path = os.path.join(folder_path, img)
                try:
                    # Corrected upload method - pass the path string directly
                    project.upload(img_path)  # Changed from file object to path string
                    success_count += 1
                except Exception as e:
                    print(f"Failed to upload {img}: {str(e)}")

            # Construct project URL manually
            project_url = f"https://app.roboflow.com/{self.workspace_name}/{project_name}"
            
            # Show success message
            messagebox.showinfo(
                "Success",
                f"{'Created' if project_created else 'Updated'} project with {success_count} images\n\n"
                f"Access your project at:\n{project_url}",
                parent=self
            )

        except Exception as e:
            messagebox.showerror(
                "Upload Error",
                f"Error during upload:\n{str(e)}\n\n"
                f"Note: {success_count} images were uploaded successfully",
                parent=self
            )
        finally:
            # Close all upload-related windows
            for window in self.winfo_children():
                if isinstance(window, tk.Toplevel) and window.title() in ["Create New Roboflow Project", "Project License"]:
                    window.destroy()

    
    def _show_roboflow_download_dialog(self):
        download_window = Toplevel(self)
        download_window.title("Download Dataset from Roboflow")
        download_window.geometry("700x500")
    
    # Add progress bar
        self.download_progress = ttk.Progressbar(download_window, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.download_progress.grid(row=7, column=0, columnspan=3, pady=10)
        
        self.download_progress = ttk.Progressbar(
            download_window, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode='determinate'
        )
        self.download_progress.grid(row=7, column=0, columnspan=3, pady=10)

        # Fetch projects data
        try:
            self.workspace_name = None
            self.API_KEY = "BAV3BZKUATBxapsB90L4"
            try:
                response = requests.get(f"https://api.roboflow.com/?api_key={self.API_KEY}")
                if response.status_code == 200:
                    self.workspace_name = response.json().get("workspace")
            except Exception as e:
                print(f"Could not fetch workspace: {str(e)}")
            response = requests.get(f"https://api.roboflow.com/{self.workspace_name}/?api_key={self.API_KEY}")
            response.raise_for_status()
            workspace_data = response.json()
            projects = workspace_data['workspace']['projects']
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch projects:\n{str(e)}", parent=download_window)
            download_window.destroy()
            return

        # Project selection
        ttk.Label(download_window, text="Select Project:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.project_var = tk.StringVar()
        project_names = [f"{p['name']} ({p['type'].replace('-', ' ').title()})" for p in projects]
        project_combobox = ttk.Combobox(
            download_window,
            textvariable=self.project_var,
            values=project_names,
            state="readonly"
        )
        project_combobox.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        project_combobox.current(0)

        # Project info display
        self.project_info = tk.Text(download_window, height=10, width=60, wrap=tk.WORD)
        self.project_info.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        scrollbar = ttk.Scrollbar(download_window, command=self.project_info.yview)
        scrollbar.grid(row=1, column=2, sticky="ns")
        self.project_info.config(yscrollcommand=scrollbar.set)

        # Version selection
        ttk.Label(download_window, text="Version:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.version_var = tk.StringVar()
        self.version_combobox = ttk.Combobox(
            download_window,
            textvariable=self.version_var,
            state="readonly"
        )
        self.version_combobox.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Format selection
        ttk.Label(download_window, text="Export Format:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.format_var = tk.StringVar(value="yolov8")
        format_combobox = ttk.Combobox(
            download_window,
            textvariable=self.format_var,
            values=["yolov8","yolov12", "coco","coco-segmentation", "tfrecord", "voc", "csv"],
            state="readonly"
        )
        format_combobox.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        # Destination folder
        ttk.Label(download_window, text="Save To:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.download_folder = tk.StringVar(value=os.getcwd())

        download_path = self.download_folder.get()
        print("the path is:", download_path)
        

        ttk.Entry(download_window, textvariable=self.download_folder, width=40).grid(
            row=4, column=1, sticky="ew", padx=10, pady=5
        )
        ttk.Button(
            download_window, 
            text="Browse", 
            command=lambda: self.download_folder.set(filedialog.askdirectory())
        ).grid(row=4, column=2, padx=5)

        # Status
        self.download_status = tk.StringVar()
        ttk.Label(download_window, textvariable=self.download_status, foreground="blue").grid(
            row=5, column=0, columnspan=3, pady=10
        )

        # Buttons
        button_frame = ttk.Frame(download_window)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)

        
        
        ttk.Button(
            button_frame,
            text="Download Dataset",
            command=lambda: self._perform_roboflow_download(projects),
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=download_window.destroy
        ).pack(side=tk.RIGHT)

        # Update project info when selection changes
        def update_project_info(event=None):
            selected_idx = project_combobox.current()
            if selected_idx >= 0:
                project = projects[selected_idx]
                info_text = (
                    f"Name: {project['name']}\n"
                    f"Type: {project['type'].replace('-', ' ').title()}\n"
                    f"Images: {project['images']}\n"
                    f"Last Updated: {datetime.fromtimestamp(project['updated']).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Classes: {', '.join([c for c in project['classes'].keys() if project['classes'][c] > 0])}\n"
                    f"Versions: {project['versions']}"
                )
                self.project_info.delete(1.0, tk.END)
                self.project_info.insert(tk.END, info_text)
                
                # Update versions
                self.version_combobox['values'] = list(range(1, project['versions'] + 1))
                if project['versions'] > 0:
                    self.version_combobox.current(project['versions'] - 1)  # Select latest version

        project_combobox.bind("<<ComboboxSelected>>", update_project_info)
        update_project_info()  # Initialize with first project

        # Configure grid weights
        download_window.rowconfigure(1, weight=1)
        download_window.columnconfigure(1, weight=1)

    def _perform_roboflow_download(self, projects):
        try:
            # Parse selected project name
            selected_idx = self.project_var.get().rfind('(')
            project_name = self.project_var.get()[:selected_idx].strip()
            version = self.version_var.get()
            export_format = self.format_var.get()
            save_path = self.download_folder.get()
            
            if not all([project_name, version, export_format, save_path]):
                self.download_status.set("All fields are required!")
                return
                
            self.download_status.set("Initializing download...")
            self.download_progress['value'] = 0
            self.update()
            
            # Initialize Roboflow
            rf = Roboflow(api_key=self.API_KEY)
            project = rf.workspace(self.workspace_name).project(project_name)
            version_obj = project.version(version)
            
            # Create download directory
            download_dir = Path(save_path) / f"{project_name}_v{version}"
            download_dir.mkdir(exist_ok=True)
            zip_path = download_dir / f"{project_name}_v{version}.zip"
            
            # Step 1: Download the dataset directly
            self.download_status.set("Downloading dataset...")
            self.download_progress['value'] = 30
            self.update()

            # Current recommended way to download datasets
            version_obj.download(
                export_format,
                location=str(download_dir),
                overwrite=True
            )
            
            # Verify the ZIP file was created
            if not zip_path.exists():
                # Fallback to check for unzipped files
                if not any(download_dir.iterdir()):
                    raise Exception("No files were downloaded")
            
            # Complete progress
            self.download_progress['value'] = 100
            self.download_status.set("Download complete!")

            # Store the actual path in database
            cursor=conn.cursor()
            cursor.execute("""
                UPDATE params 
                SET DatasetPath = ? 
                WHERE id = ?
            """, (str(download_dir), settings_id))
            conn.commit()
            print(f"Updated Dataset Path to: {download_dir}")
            
            messagebox.showinfo(
                "Success",
                f"Dataset downloaded successfully to:\n{download_dir}",
                parent=self
            )
            
        except Exception as e:
            # Clean up partial download
            if 'download_dir' in locals():
                try:
                    shutil.rmtree(download_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    print(f"Cleanup failed: {cleanup_error}")
                    
            self.download_progress['value'] = 0
            messagebox.showerror(
                "Download Error",
                f"Failed to download dataset:\n{str(e)}",
                parent=self
            )
            self.download_status.set("Download failed")

    def _prepare_training(self):
        train_window = Toplevel(self)
        train_window.title("Train Model Configuration")
        train_window.geometry("800x600")
        
        # Get the last downloaded dataset path
        last_download_path = self._get_last_download_path()
        
        # Training Script
        ttk.Label(train_window, text="Training Script:").grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Set a fixed path instead of taking user input
        self.train_script_var = tk.StringVar(value="path/to/your/script.py")  # Hardcoded path

        # Display the path in a Label instead of an Entry widget
        ttk.Label(train_window, textvariable=self.train_script_var, width=40).grid(
            row=0, column=1, sticky="w", padx=10, pady=5
        )
        ttk.Button(
            train_window, 
            text="Browse", 
            command=lambda: self.train_script_var.set(filedialog.askopenfilename(
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
            ))
        ).grid(row=0, column=2, padx=5)
        
        # Display dataset path (read-only)
        ttk.Label(train_window, text="Using Dataset:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(train_window, text=last_download_path).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Training parameters
        ttk.Label(train_window, text="Epochs:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.epochs_var = tk.StringVar(value="50")
        ttk.Entry(train_window, textvariable=self.epochs_var, width=10).grid(
            row=2, column=1, sticky="w", padx=10, pady=5
        )
        
        ttk.Label(train_window, text="Batch Size:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.batch_size_var = tk.StringVar(value="16")
        ttk.Entry(train_window, textvariable=self.batch_size_var, width=10).grid(
            row=3, column=1, sticky="w", padx=10, pady=5
        )
        
        # Buttons
        button_frame = ttk.Frame(train_window)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(
            button_frame,
            text="Start Training",
            command=lambda: self._start_training(train_window, last_download_path),
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=train_window.destroy
        ).pack(side=tk.RIGHT)

    def _get_last_download_path(self):
        """Get the path from the last Roboflow download"""
        cursor = conn.cursor()
        cursor.execute("SELECT DatasetPath FROM params WHERE id = ?", (1,))
        path = cursor.fetchall()
        print("path is ",path)
        return path

    def _start_training(self, window, dataset_path):
        train_script = self.train_script_var.get()
        epochs = self.epochs_var.get()
        batch_size = self.batch_size_var.get()
        
        if not all([train_script, epochs, batch_size]):
            messagebox.showerror("Error", "All fields are required!", parent=window)
            return
        
        if not Path(train_script).exists():
            messagebox.showerror("Error", "Training script does not exist!", parent=window)
            return
        
        # Save config
        config = {
            "train_script": train_script,
            "dataset_path": dataset_path,
            "epochs": int(epochs),
            "batch_size": int(batch_size),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # with open("training_config.json", "w") as f:
        #     json.dump(config, f, indent=4)
        
        # Open new console window for training output
        cursor=conn.cursor()
        cursor.execute("""
            UPDATE params 
            SET Epochs = ? 
            WHERE id = ?
        """, (epochs, settings_id))
        conn.commit()
        
        self._run_training_in_console(train_script, dataset_path, epochs, batch_size)
        window.destroy()

    def _run_training_in_console(self, script_path, dataset_path, epochs, batch_size):
        """Run training in a separate console window"""
        try:
            # Convert all arguments to strings and normalize paths
            script_path = os.path.normpath(str(script_path))
            dataset_path = os.path.normpath(str(dataset_path))
            epochs = str(epochs)
            batch_size = str(batch_size)
            
            # Platform-specific command construction
            if os.name == 'nt':  # Windows
                # Windows needs the whole command as a single string
                cmd = f'python "{script_path}" --data "{dataset_path}" --epochs {epochs} --batch-size {batch_size}'
                subprocess.Popen(['start', 'cmd', '/k', cmd], shell=True)
            else:  # Linux/Mac
                # Linux/Mac needs proper list format
                cmd = [
                    'x-terminal-emulator',
                    '-e',
                    'bash',
                    '-c',
                    f'python "{script_path}" --data "{dataset_path}" --epochs {epochs} --batch-size {batch_size}; exec bash'
                ]
                subprocess.Popen(cmd)
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to start training:\n{str(e)}",
                parent=self
            )

    def show_about(self):
        about_window = Toplevel(self)
        about_window.title("About Tile Inspection System")
        about_window.geometry("400x200")
        
        ttk.Label(
            about_window,
            text="Tile Inspection System\n\nVersion 1.0\n\nDeveloped for tile quality inspection",
            justify=tk.CENTER,
            padding=20
        ).pack(expand=True)
        
        ttk.Button(
            about_window,
            text="Close",
            command=about_window.destroy
        ).pack(pady=10)

if __name__ == "__main__":
    app = Application()
    app.mainloop()