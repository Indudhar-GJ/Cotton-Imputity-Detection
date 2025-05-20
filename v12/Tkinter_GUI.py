import tkinter as tk
from tkinter import messagebox, filedialog, ttk, Toplevel
import subprocess
import threading
import time
import os
import shutil
from PIL import Image, ImageTk
import json

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
        try:
            subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
            messagebox.showinfo("Success", "All dependencies installed successfully!")
            self.status_var.set("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to install dependencies: {str(e)}")
            self.status_var.set("Dependency installation failed")
    
    def upload_model(self):
        file_path = filedialog.askopenfilename(
            title="Select a Model File",
            filetypes=[
                ("Model Files", "*.pt *.engine"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
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

    def upload_model(self):
        file_path = filedialog.askopenfilename(
            title="Select a Model File",
            filetypes=[
                ("Model Files", "*.pt *.engine"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            try:
                self.current_model_path = file_path
                messagebox.showinfo("Success", f"Model file loaded successfully!\n{file_path}")
                self.status_var.set(f"Model loaded: {os.path.basename(file_path)}")
                self.save_config()  # Save after uploading model
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model: {str(e)}")
                self.status_var.set("Model loading failed")
    
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