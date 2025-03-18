import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from datetime import datetime

class RuneSlayerDupe:
    def __init__(self, root):
        self.root = root
        self.root.title("RuneSlayer Dupe Tool")
        self.root.geometry("700x500")
        self.root.configure(bg="#2c2f33")
        
        # Check if launched through loader
        if not self.verify_launch():
            messagebox.showerror("Unauthorized Access", "This tool must be launched through the RuneSlayer Loader.")
            self.root.destroy()
            return
        
        self.setup_ui()
    
    def verify_launch(self):
        """Verify that the tool was launched through the loader"""
        # In a real implementation, you would add more sophisticated checks
        # This is a simple example
        temp_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.basename(temp_dir) == "temp"
    
    def setup_ui(self):
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.dupe_tab = tk.Frame(self.notebook, bg="#36393f")
        self.settings_tab = tk.Frame(self.notebook, bg="#36393f")
        
        self.notebook.add(self.dupe_tab, text="Dupe Tool")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Setup dupe tab
        self.setup_dupe_tab()
        # Setup settings tab
        self.setup_settings_tab()
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#2c2f33", fg="#ffffff")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_dupe_tab(self):
        # Title
        title_label = tk.Label(self.dupe_tab, text="RuneSlayer Dupe Tool", font=("Arial", 16, "bold"), bg="#36393f", fg="#ffffff")
        title_label.pack(pady=10)
        
        # Game selection frame
        game_frame = tk.Frame(self.dupe_tab, bg="#36393f")
        game_frame.pack(pady=5, fill=tk.X, padx=20)
        
        game_label = tk.Label(game_frame, text="Select Game:", bg="#36393f", fg="#ffffff")
        game_label.pack(side=tk.LEFT, padx=5)
        
        self.game_var = tk.StringVar()
        games = ["Rune Legacy", "Rune Classic", "RuneScape 3"]
        self.game_combobox = ttk.Combobox(game_frame, textvariable=self.game_var, values=games, width=30)
        self.game_combobox.current(0)
        self.game_combobox.pack(side=tk.LEFT, padx=5)
        
        # File selection frame
        file_frame = tk.Frame(self.dupe_tab, bg="#36393f")
        file_frame.pack(pady=5, fill=tk.X, padx=20)
        
        file_label = tk.Label(file_frame, text="Save File:", bg="#36393f", fg="#ffffff")
        file_label.pack(side=tk.LEFT, padx=5)
        
        self.file_entry = tk.Entry(file_frame, width=40, bg="#40444b", fg="#ffffff", insertbackground="#ffffff")
        self.file_entry.pack(side=tk.LEFT, padx=5)
        
        browse_button = tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#7289da", fg="#ffffff")
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Options frame
        options_frame = tk.LabelFrame(self.dupe_tab, text="Dupe Options", bg="#36393f", fg="#ffffff")
        options_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Item selection
        item_frame = tk.Frame(options_frame, bg="#36393f")
        item_frame.pack(pady=5, fill=tk.X)
        
        item_label = tk.Label(item_frame, text="Item to Dupe:", bg="#36393f", fg="#ffffff", width=12, anchor="w")
        item_label.pack(side=tk.LEFT, padx=5)
        
        self.item_var = tk.StringVar()
        items = ["Gold", "Runes", "Weapons", "Armor", "All Items"]
        self.item_combobox = ttk.Combobox(item_frame, textvariable=self.item_var, values=items, width=30)
        self.item_combobox.current(0)
        self.item_combobox.pack(side=tk.LEFT, padx=5)
        
        # Quantity frame
        quantity_frame = tk.Frame(options_frame, bg="#36393f")
        quantity_frame.pack(pady=5, fill=tk.X)
        
        quantity_label = tk.Label(quantity_frame, text="Quantity:", bg="#36393f", fg="#ffffff", width=12, anchor="w")
        quantity_label.pack(side=tk.LEFT, padx=5)
        
        self.quantity_var = tk.StringVar(value="1")
        quantity_entry = tk.Entry(quantity_frame, textvariable=self.quantity_var, width=10, bg="#40444b", fg="#ffffff", insertbackground="#ffffff")
        quantity_entry.pack(side=tk.LEFT, padx=5)
        
        # Method frame
        method_frame = tk.Frame(options_frame, bg="#36393f")
        method_frame.pack(pady=5, fill=tk.X)
        
        method_label = tk.Label(method_frame, text="Dupe Method:", bg="#36393f", fg="#ffffff", width=12, anchor="w")
        method_label.pack(side=tk.LEFT, padx=5)
        
        self.method_var = tk.StringVar()
        methods = ["Packet Injection", "Save Rollback", "Trade Exploit", "Server Lag"]
        self.method_combobox = ttk.Combobox(method_frame, textvariable=self.method_var, values=methods, width=30)
        self.method_combobox.current(0)
        self.method_combobox.pack(side=tk.LEFT, padx=5)
        
        # Safety options
        safety_frame = tk.Frame(options_frame, bg="#36393f")
        safety_frame.pack(pady=5, fill=tk.X)
        
        self.safe_mode_var = tk.BooleanVar(value=True)
        safe_mode_check = tk.Checkbutton(safety_frame, text="Safe Mode (Reduces Ban Risk)", variable=self.safe_mode_var, bg="#36393f", fg="#ffffff", selectcolor="#2c2f33", activebackground="#36393f")
        safe_mode_check.pack(side=tk.LEFT, padx=5)
        
        self.auto_logout_var = tk.BooleanVar(value=True)
        auto_logout_check = tk.Checkbutton(safety_frame, text="Auto-Logout After Dupe", variable=self.auto_logout_var, bg="#36393f", fg="#ffffff", selectcolor="#2c2f33", activebackground="#36393f")
        auto_logout_check.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        progress_frame = tk.Frame(self.dupe_tab, bg="#36393f")
        progress_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X)
        
        self.progress_label = tk.Label(progress_frame, text="Ready to dupe", bg="#36393f", fg="#ffffff")
        self.progress_label.pack(pady=5)
        
        # Action buttons
        button_frame = tk.Frame(self.dupe_tab, bg="#36393f")
        button_frame.pack(pady=10)
        
        start_button = tk.Button(button_frame, text="Start Dupe", command=self.start_dupe, bg="#43b581", fg="#ffffff", width=15)
        start_button.pack(side=tk.LEFT, padx=5)
        
        stop_button = tk.Button(button_frame, text="Stop", command=self.stop_dupe, bg="#f04747", fg="#ffffff", width=15)
        stop_button.pack(side=tk.LEFT, padx=5)
    
    def setup_settings_tab(self):
        # Settings title
        title_label = tk.Label(self.settings_tab, text="Settings", font=("Arial", 16, "bold"), bg="#36393f", fg="#ffffff")
        title_label.pack(pady=10)
        
        # Connection settings
        connection_frame = tk.LabelFrame(self.settings_tab, text="Connection", bg="#36393f", fg="#ffffff")
        connection_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Server address
        server_frame = tk.Frame(connection_frame, bg="#36393f")
        server_frame.pack(pady=5, fill=tk.X)
        
        server_label = tk.Label(server_frame, text="Server:", bg="#36393f", fg="#ffffff", width=12, anchor="w")
        server_label.pack(side=tk.LEFT, padx=5)
        
        self.server_var = tk.StringVar(value="auto")
        server_entry = tk.Entry(server_frame, textvariable=self.server_var, width=30, bg="#40444b", fg="#ffffff", insertbackground="#ffffff")
        server_entry.pack(side=tk.LEFT, padx=5)
        
        # Port
        port_frame = tk.Frame(connection_frame, bg="#36393f")
        port_frame.pack(pady=5, fill=tk.X)
        
        port_label = tk.Label(port_frame, text="Port:", bg="#36393f", fg="#ffffff", width=12, anchor="w")
        port_label.pack(side=tk.LEFT, padx=5)
        
        self.port_var = tk.StringVar(value="43594")
        port_entry = tk.Entry(port_frame, textvariable=self.port_var, width=10, bg="#40444b", fg="#ffffff", insertbackground="#ffffff")
        port_entry.pack(side=tk.LEFT, padx=5)
        
        # Proxy settings
        proxy_frame = tk.Frame(connection_frame, bg="#36393f")
        proxy_frame.pack(pady=5, fill=tk.X)
        
        self.use_proxy_var = tk.BooleanVar(value=False)
        proxy_check = tk.Checkbutton(proxy_frame, text="Use Proxy", variable=self.use_proxy_var, bg="#36393f", fg="#ffffff", selectcolor="#2c2f33", activebackground="#36393f")
        proxy_check.pack(side=tk.LEFT, padx=5)
        
        self.proxy_var = tk.StringVar()
        proxy_entry = tk.Entry(proxy_frame, textvariable=self.proxy_var, width=30, bg="#40444b", fg="#ffffff", insertbackground="#ffffff")
        proxy_entry.pack(side=tk.LEFT, padx=5)
        
        # Advanced settings
        advanced_frame = tk.LabelFrame(self.settings_tab, text="Advanced", bg="#36393f", fg="#ffffff")
        advanced_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Timeout
        timeout_frame = tk.Frame(advanced_frame, bg="#36393f")
        timeout_frame.pack(pady=5, fill=tk.X)
        
        timeout_label = tk.Label(timeout_frame, text="Timeout (ms):", bg="#36393f", fg="#ffffff", width=12, anchor="w")
        timeout_label.pack(side=tk.LEFT, padx=5)
        
        self.timeout_var = tk.StringVar(value="5000")
        timeout_entry = tk.Entry(timeout_frame, textvariable=self.timeout_var, width=10, bg="#40444b", fg="#ffffff", insertbackground="#ffffff")
        timeout_entry.pack(side=tk.LEFT, padx=5)
        
        # Debug mode
        debug_frame = tk.Frame(advanced_frame, bg="#36393f")
        debug_frame.pack(pady=5, fill=tk.X)
        
        self.debug_var = tk.BooleanVar(value=False)
        debug_check = tk.Checkbutton(debug_frame, text="Debug Mode", variable=self.debug_var, bg="#36393f", fg="#ffffff", selectcolor="#2c2f33", activebackground="#36393f")
        debug_check.pack(side=tk.LEFT, padx=5)
        
        # Save settings button
        save_button = tk.Button(self.settings_tab, text="Save Settings", command=self.save_settings, bg="#7289da", fg="#ffffff", width=15)
        save_button.pack(pady=10)
    
    def browse_file(self):
        """Open file browser dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Save File",
            filetypes=(("Save Files", "*.sav"), ("All Files", "*.*"))
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
    
    def start_dupe(self):
        """Start the duplication process"""
        # Get values
        game = self.game_var.get()
        save_file = self.file_entry.get()
        item = self.item_var.get()
        quantity = self.quantity_var.get()
        method = self.method_var.get()
        
        # Validate inputs
        if not save_file:
            messagebox.showerror("Error", "Please select a save file.")
            return
        
        if not os.path.exists(save_file):
            messagebox.showerror("Error", "Save file not found.")
            return
        
        # Simulate duplication process
        self.status_bar.config(text=f"Duping {quantity}x {item} in {game}...")
        
        # Reset progress bar
        self.progress['value'] = 0
        self.progress_label.config(text="Initializing...")
        self.root.update()
        
        # Simulate steps
        steps = ["Analyzing save file", "Preparing dupe method", "Creating backup", 
                "Identifying item data", "Modifying memory", "Applying changes", 
                "Verifying results", "Cleaning up traces"]
        
        step_increment = 100 / len(steps)
        
        for step in steps:
            # Update progress
            self.progress_label.config(text=step)
            self.root.update()
            
            # Simulate processing time
            self.root.after(500)
            
            # Increment progress bar
            self.progress['value'] += step_increment
            self.root.update()
        
        # Complete
        self.progress['value'] = 100
        self.progress_label.config(text=f"Successfully duped {quantity}x {item}!")
        self.status_bar.config(text="Dupe completed successfully")
        
        messagebox.showinfo("Success", f"Successfully duped {quantity}x {item} in {game}!")
    
    def stop_dupe(self):
        """Stop the duplication process"""
        self.progress['value'] = 0
        self.progress_label.config(text="Process stopped")
        self.status_bar.config(text="Ready")
        messagebox.showinfo("Stopped", "Duplication process has been stopped.")
    
    def save_settings(self):
        """Save the current settings"""
        settings = {
            "server": self.server_var.get(),
            "port": self.port_var.get(),
            "use_proxy": self.use_proxy_var.get(),
            "proxy": self.proxy_var.get(),
            "timeout": self.timeout_var.get(),
            "debug": self.debug_var.get()
        }
        
        # In a real implementation, you would save this to a file
        print("Saving settings:")
        print(json.dumps(settings, indent=2))
        
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RuneSlayerDupe(root)
    root.mainloop()
