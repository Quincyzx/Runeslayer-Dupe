#!/usr/bin/env python3
"""
Tact Tool - Main Application
Handles user authentication and tool functionality with updated UI
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from PIL import Image, ImageTk
import os.path

# Import our modules
from auth_utils import verify_license, update_usage, get_system_id
from ui_helpers import HoverButton, create_tooltip

# Constants
PRIMARY_COLOR = "#cb6ce6"  # Tact brand color
BACKGROUND_COLOR = "#1a1a1a"
TEXT_COLOR = "#ffffff"
KEYS_FILE = "keys.json"
LOGO_URL = "https://github.com/Quincyzx/Runeslayer-Dupe/raw/main/Tact.png"

class TactTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Tact Tool")
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.resizable(False, False)
        
        # Set window size and position
        self.root.geometry("600x500")
        self.center_window()
        
        # Try to set window icon using the logo URL
        try:
            # Load logo directly from URL for icon
            response = requests.get(LOGO_URL, stream=True)
            if response.status_code == 200:
                from io import BytesIO
                icon_img = Image.open(BytesIO(response.content))
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, icon_photo)
        except Exception as e:
            print(f"Error setting window icon: {e}")
        
        # Authentication state
        self.authenticated = False
        self.user_data = None
        self.license_key = None
        
        # Set up styling
        self.setup_styles()
        
        # Show authentication UI first
        self.setup_auth_ui()
        
        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def setup_styles(self):
        """Set up custom ttk styles"""
        style = ttk.Style(self.root)
        style.configure("TNotebook", background=BACKGROUND_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background="#333333", foreground=TEXT_COLOR, padding=[10, 5], font=("Arial", 10))
        style.map("TNotebook.Tab", 
                 background=[("selected", PRIMARY_COLOR)],
                 foreground=[("selected", "white")])
        style.configure("TFrame", background=BACKGROUND_COLOR)
        style.configure("TLabel", background=BACKGROUND_COLOR, foreground=TEXT_COLOR)
        style.configure("TButton", 
                        background=PRIMARY_COLOR, 
                        foreground="white", 
                        borderwidth=0,
                        font=("Arial", 10, "bold"))
        style.configure("Secondary.TButton", 
                        background="#555555", 
                        foreground="white", 
                        borderwidth=0,
                        font=("Arial", 10))
        style.map("TButton", 
                 background=[("active", PRIMARY_COLOR), ("disabled", "#888888")],
                 foreground=[("active", "white"), ("disabled", "#cccccc")])
    
    def setup_auth_ui(self):
        """Set up the authentication UI"""
        # Clear any existing UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main frame
        self.auth_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.auth_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo
        self.logo_frame = tk.Frame(self.auth_frame, bg=BACKGROUND_COLOR)
        self.logo_frame.pack(pady=20)
        
        try:
            # Load logo directly from URL
            response = requests.get(LOGO_URL, stream=True)
            if response.status_code == 200:
                from io import BytesIO
                logo_img = Image.open(BytesIO(response.content))
                logo_img = logo_img.resize((120, 120), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(self.logo_frame, image=self.logo_image, bg=BACKGROUND_COLOR)
                logo_label.pack()
            else:
                # Fallback if logo URL is unreachable
                logo_label = tk.Label(
                    self.logo_frame, 
                    text="TACT", 
                    font=("Arial", 36, "bold"), 
                    fg=PRIMARY_COLOR, 
                    bg=BACKGROUND_COLOR
                )
                logo_label.pack()
                print(f"Failed to load logo from URL: {response.status_code}")
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback if logo loading fails
            logo_label = tk.Label(
                self.logo_frame, 
                text="TACT", 
                font=("Arial", 36, "bold"), 
                fg=PRIMARY_COLOR, 
                bg=BACKGROUND_COLOR
            )
            logo_label.pack()
        
        # License key input frame
        self.input_frame = tk.Frame(self.auth_frame, bg=BACKGROUND_COLOR)
        self.input_frame.pack(pady=20)
        
        self.key_label = tk.Label(
            self.input_frame, 
            text="Enter License Key", 
            font=("Arial", 12), 
            fg=TEXT_COLOR, 
            bg=BACKGROUND_COLOR
        )
        self.key_label.pack()
        
        self.key_entry = tk.Entry(
            self.input_frame, 
            width=30, 
            font=("Arial", 12),
            bg="#333333",
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief=tk.FLAT,
            justify='center'
        )
        self.key_entry.pack(pady=10)
        create_tooltip(self.key_entry, "Enter your license key in the format XXXX-XXXX-XXXX-XXXX")
        
        # Status message
        self.status_frame = tk.Frame(self.auth_frame, bg=BACKGROUND_COLOR)
        self.status_frame.pack(pady=5)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="",
            font=("Arial", 10),
            fg="#FF5555",
            bg=BACKGROUND_COLOR
        )
        self.status_label.pack()
        
        # Buttons
        self.button_frame = tk.Frame(self.auth_frame, bg=BACKGROUND_COLOR)
        self.button_frame.pack(pady=20)
        
        self.login_button = HoverButton(
            self.button_frame,
            text="Activate License",
            command=self.login,
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            relief=tk.FLAT
        )
        self.login_button.pack(side=tk.LEFT, padx=10)
        
        self.exit_button = HoverButton(
            self.button_frame,
            text="Exit",
            command=self.exit_application,
            bg="#555555",
            fg="white",
            font=("Arial", 11),
            width=10,
            relief=tk.FLAT
        )
        self.exit_button.pack(side=tk.LEFT, padx=10)
        
        # System ID info (hidden initially)
        self.system_frame = tk.Frame(self.auth_frame, bg=BACKGROUND_COLOR)
        self.system_frame.pack(pady=10, side=tk.BOTTOM)
        
        self.hwid_label = tk.Label(
            self.system_frame,
            text=f"System ID: {get_system_id()}",
            font=("Arial", 8),
            fg="#777777",
            bg=BACKGROUND_COLOR
        )
        self.hwid_label.pack()
        
        # Set focus to the key entry
        self.key_entry.focus_set()
        
        # Bind Enter key to login
        self.key_entry.bind("<Return>", lambda event: self.login())
    
    def login(self):
        """Handle login attempt with visual feedback"""
        # Get key and remove whitespace
        key = self.key_entry.get().strip()
        
        if not key:
            self.status_label.config(text="Please enter a license key")
            return
        
        # Disable login button and show status
        self.login_button.config(state=tk.DISABLED)
        self.status_label.config(text="Verifying license...", fg="#FFAA33")
        self.root.update()
        
        # Verify license in background thread to keep UI responsive
        threading.Thread(target=self._verify_license, args=(key,), daemon=True).start()
    
    def _verify_license(self, key):
        """Verify license in background thread with better error handling"""
        try:
            # Verify the license
            success, user_data, message = verify_license(key, KEYS_FILE)
            
            # Update UI from main thread
            self.root.after(0, lambda: self._update_login_ui(success, user_data, message, key))
        except Exception as e:
            error_msg = f"Verification error: {str(e)}"
            self.root.after(0, lambda: self._update_login_ui(False, None, error_msg, key))
            
        if not success:
            # Log failed attempts for security
            print(f"Failed login attempt with key: {key[:4]}***")
    
    def _update_login_ui(self, success, user_data, message, key):
        """Update login UI based on verification result"""
        if success:
            # Store authentication state
            self.authenticated = True
            self.user_data = user_data
            self.license_key = key
            
            # Show success message
            self.status_label.config(text="License verified successfully", fg="#55FF55")
            
            # Update usage count
            update_success, _ = update_usage(key, KEYS_FILE)
            if not update_success:
                print("Warning: Failed to update usage count")
            
            # After short delay, switch to main UI
            self.root.after(1000, self.setup_main_ui)
        else:
            # Show error message
            self.status_label.config(text=message, fg="#FF5555")
            self.login_button.config(state=tk.NORMAL)
    
    def setup_main_ui(self):
        """Set up the main UI after authentication"""
        # Clear any existing UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with logo
        self.header_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        self.header_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Try to load smaller logo for header
        try:
            # Load logo directly from URL for header
            response = requests.get(LOGO_URL, stream=True)
            if response.status_code == 200:
                from io import BytesIO
                logo_img = Image.open(BytesIO(response.content))
                logo_img = logo_img.resize((40, 40), Image.LANCZOS)
                self.small_logo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(self.header_frame, image=self.small_logo, bg=BACKGROUND_COLOR)
                logo_label.pack(side=tk.LEFT, padx=10)
            
            # User info
            if self.user_data and 'name' in self.user_data:
                user_label = tk.Label(
                    self.header_frame,
                    text=f"Welcome, {self.user_data['name']}",
                    font=("Arial", 10, "bold"),
                    fg=TEXT_COLOR,
                    bg=BACKGROUND_COLOR
                )
                user_label.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            print(f"Error in header setup: {e}")
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.profile_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text="Tools")
        self.notebook.add(self.profile_tab, text="Profile")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Set up tab content
        self.setup_main_tab()
        self.setup_profile_tab()
        self.setup_settings_tab()
        
        # Footer
        self.create_footer()
    
    def create_footer(self):
        """Create application footer"""
        self.footer_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Exit button
        self.exit_btn = HoverButton(
            self.footer_frame,
            text="Exit",
            command=self.exit_application,
            bg="#555555",
            fg="white",
            font=("Arial", 9),
            relief=tk.FLAT
        )
        self.exit_btn.pack(side=tk.RIGHT, padx=10)
        
        # Add copyright
        copyright_label = tk.Label(
            self.footer_frame,
            text="© 2025 Tact Technologies",
            font=("Arial", 8),
            fg="#777777",
            bg=BACKGROUND_COLOR
        )
        copyright_label.pack(side=tk.LEFT, padx=10)
    
    def setup_profile_tab(self):
        """Set up the profile tab content"""
        # Frame for profile info
        profile_frame = tk.Frame(self.profile_tab, bg=BACKGROUND_COLOR)
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Profile header
        header_label = tk.Label(
            profile_frame,
            text="License Information",
            font=("Arial", 14, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=(0, 20))
        
        # Info box
        info_box = tk.Frame(profile_frame, bg="#333333", padx=20, pady=20)
        info_box.pack(fill=tk.X)
        
        # Display user information
        row = 0
        if self.user_data:
            self.create_info_row(info_box, "License Key", self.license_key, row)
            row += 1
            
            if 'name' in self.user_data:
                self.create_info_row(info_box, "Name", self.user_data['name'], row)
                row += 1
            
            if 'expires' in self.user_data:
                self.create_info_row(info_box, "Expiration Date", self.user_data['expires'], row)
                row += 1
            
            if 'uses_remaining' in self.user_data:
                self.create_info_row(info_box, "Uses Remaining", str(self.user_data['uses_remaining']), row)
                row += 1
        
        self.create_info_row(info_box, "System ID", get_system_id(), row)
    
    def create_info_row(self, parent, label, value, row):
        """Create a row of information in the profile tab"""
        label_widget = tk.Label(
            parent,
            text=f"{label}:",
            font=("Arial", 10, "bold"),
            fg=TEXT_COLOR,
            bg="#333333",
            anchor="w"
        )
        label_widget.grid(row=row, column=0, sticky="w", pady=5)
        
        value_widget = tk.Label(
            parent,
            text=value,
            font=("Arial", 10),
            fg=TEXT_COLOR,
            bg="#333333",
            anchor="w"
        )
        value_widget.grid(row=row, column=1, sticky="w", padx=20, pady=5)
    
    def setup_main_tab(self):
        """Set up the main tab content"""
        # Main tools frame
        tools_frame = tk.Frame(self.main_tab, bg=BACKGROUND_COLOR)
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tools header
        header_label = tk.Label(
            tools_frame,
            text="Available Tools",
            font=("Arial", 14, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=(0, 20))
        
        # Grid for tool buttons
        buttons_frame = tk.Frame(tools_frame, bg=BACKGROUND_COLOR)
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tool buttons
        tools = [
            {"name": "Network Scanner", "description": "Scan network for devices", "function": "network_scan"},
            {"name": "Password Generator", "description": "Generate secure passwords", "function": "password_gen"},
            {"name": "System Analyzer", "description": "Analyze system performance", "function": "system_analyze"},
            {"name": "Update Check", "description": "Check for software updates", "function": "check_updates"}
        ]
        
        # Create buttons in a grid
        for i, tool in enumerate(tools):
            row, col = divmod(i, 2)
            
            # Tool frame
            tool_frame = tk.Frame(buttons_frame, bg="#333333", padx=10, pady=10)
            tool_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Tool name
            name_label = tk.Label(
                tool_frame,
                text=tool["name"],
                font=("Arial", 12, "bold"),
                fg=PRIMARY_COLOR,
                bg="#333333"
            )
            name_label.pack(anchor="w")
            
            # Tool description
            desc_label = tk.Label(
                tool_frame,
                text=tool["description"],
                font=("Arial", 10),
                fg=TEXT_COLOR,
                bg="#333333"
            )
            desc_label.pack(anchor="w", pady=(0, 10))
            
            # Tool button
            tool_btn = HoverButton(
                tool_frame,
                text="Run",
                command=lambda f=tool["function"]: self.run_tool_function(f),
                bg=PRIMARY_COLOR,
                fg="white",
                font=("Arial", 10),
                width=8,
                relief=tk.FLAT
            )
            tool_btn.pack(anchor="e")
        
        # Make grid cells expandable
        for i in range(2):
            buttons_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            buttons_frame.grid_rowconfigure(i, weight=1)
    
    def run_tool_function(self, function_name):
        """Run a tool function and show a message"""
        # In a real application, this would run the actual tool function
        # For now, just show a message
        messagebox.showinfo(
            "Tool Activated", 
            f"Tool function '{function_name}' was activated.\nThis is a demonstration version."
        )
    
    def setup_settings_tab(self):
        """Set up the settings tab content"""
        # Settings frame
        settings_frame = tk.Frame(self.settings_tab, bg=BACKGROUND_COLOR)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Settings header
        header_label = tk.Label(
            settings_frame,
            text="Application Settings",
            font=("Arial", 14, "bold"),
            fg=PRIMARY_COLOR,
            bg=BACKGROUND_COLOR
        )
        header_label.pack(pady=(0, 20))
        
        # Settings options
        options_frame = tk.Frame(settings_frame, bg="#333333", padx=20, pady=20)
        options_frame.pack(fill=tk.X)
        
        # Checkboxes for settings
        self.autostart_var = tk.BooleanVar(value=False)
        autostart_cb = ttk.Checkbutton(
            options_frame,
            text="Start application automatically with system",
            variable=self.autostart_var,
            style="TCheckbutton"
        )
        autostart_cb.pack(anchor="w", pady=5)
        
        self.remember_var = tk.BooleanVar(value=True)
        remember_cb = ttk.Checkbutton(
            options_frame,
            text="Remember license key",
            variable=self.remember_var,
            style="TCheckbutton"
        )
        remember_cb.pack(anchor="w", pady=5)
        
        self.updates_var = tk.BooleanVar(value=True)
        updates_cb = ttk.Checkbutton(
            options_frame,
            text="Check for updates automatically",
            variable=self.updates_var,
            style="TCheckbutton"
        )
        updates_cb.pack(anchor="w", pady=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(settings_frame, bg=BACKGROUND_COLOR)
        buttons_frame.pack(pady=20)
        
        # Save button
        save_btn = HoverButton(
            buttons_frame,
            text="Save Settings",
            command=lambda: self.save_settings(
                self.autostart_var.get(),
                self.remember_var.get(),
                self.updates_var.get()
            ),
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Arial", 10),
            width=12,
            relief=tk.FLAT
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_btn = HoverButton(
            buttons_frame,
            text="Reset to Defaults",
            command=self.reset_settings,
            bg="#555555",
            fg="white",
            font=("Arial", 10),
            width=15,
            relief=tk.FLAT
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def save_settings(self, autostart, remember, updates):
        """Save user settings"""
        # In a real application, this would save settings to a file
        # For now, just show a message
        messagebox.showinfo(
            "Settings Saved", 
            "Your settings have been saved.\n\n"
            f"Start automatically: {'Yes' if autostart else 'No'}\n"
            f"Remember license key: {'Yes' if remember else 'No'}\n"
            f"Check for updates: {'Yes' if updates else 'No'}"
        )
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.autostart_var.set(False)
        self.remember_var.set(True)
        self.updates_var.set(True)
        
        messagebox.showinfo("Settings Reset", "Settings have been reset to defaults.")
    
    def exit_application(self):
        """Exit the application with confirmation"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.cleanup()
            self.root.destroy()
    
    def cleanup(self):
        """Clean up temporary files"""
        # In a real application, this would clean up any temporary files or resources
        pass

def main():
    root = tk.Tk()
    app = TactTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
