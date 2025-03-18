#!/usr/bin/env python3
"""
Tact Tool - Main Application
Handles user authentication and tool functionality
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox
import time
import datetime
import tempfile
import atexit
from auth_utils import verify_license, update_usage

# Configuration
APP_TITLE = "Tact Tool"
VERSION = "1.0"

# Color theme - Discord inspired
COLORS = {
    "background": "#36393F",
    "background_secondary": "#2F3136",
    "text": "#DCDDDE",
    "text_muted": "#72767D",
    "text_bright": "#FFFFFF",
    "primary": "#5865F2",
    "primary_hover": "#4752C4",
    "success": "#43B581",
    "warning": "#FAA61A",
    "danger": "#F04747",
    "danger_hover": "#d04040",  # Added hover color for danger button
    "border": "#42454A",
    "input_bg": "#40444B"
}

class TactTool:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        self.root.configure(bg=COLORS["background"])

        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Variables
        self.script_dir = os.environ.get("TACT_SCRIPT_DIR", os.path.dirname(__file__))
        self.keys_file = os.path.join(self.script_dir, "keys.json")
        self.license_key = None
        self.user_info = None

        # Set up authentication UI
        self.setup_auth_ui()

        # Register cleanup
        if os.environ.get("TACT_CLEANUP_ON_EXIT") == "1":
            atexit.register(self.cleanup)

    def setup_auth_ui(self):
        """Set up the authentication UI"""
        # Main container
        self.auth_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.auth_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400)

        # Title
        title_label = tk.Label(
            self.auth_frame,
            text="Tact Tool",
            font=("Arial", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(pady=(0, 20))

        # License key entry
        key_frame = tk.Frame(self.auth_frame, bg=COLORS["background"])
        key_frame.pack(pady=(0, 20), fill=tk.X)

        key_label = tk.Label(
            key_frame,
            text="License Key:",
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        key_label.pack(side=tk.LEFT, padx=(0, 10))

        self.key_entry = tk.Entry(
            key_frame,
            bg=COLORS["input_bg"],
            fg=COLORS["text_bright"],
            insertbackground=COLORS["text_bright"],
            relief=tk.FLAT,
            width=30
        )
        self.key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Login button
        self.login_button = tk.Button(
            self.auth_frame,
            text="Login",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.login
        )
        self.login_button.pack(pady=(0, 20))

        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Enter your license key to continue")

        status_label = tk.Label(
            self.auth_frame,
            textvariable=self.status_var,
            bg=COLORS["background"],
            fg=COLORS["text_muted"],
            wraplength=400
        )
        status_label.pack()

    def login(self):
        """Handle login attempt"""
        key = self.key_entry.get().strip()
        if not key:
            self.status_var.set("Please enter a license key")
            return

        # Verify license
        success, user_data, message = verify_license(key, self.keys_file)

        if success:
            self.license_key = key
            self.user_info = user_data

            # Update usage count
            update_success, update_message = update_usage(key, self.keys_file)
            if not update_success:
                messagebox.showwarning("Warning", f"Usage tracking error: {update_message}")

            # Switch to main UI
            self.setup_main_ui()
        else:
            self.status_var.set(f"Authentication failed: {message}")

    def setup_main_ui(self):
        """Set up the main UI after authentication"""
        # Remove authentication UI
        self.auth_frame.destroy()

        # Create main UI
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=400)

        # Title with key info
        title_text = f"Welcome - {self.license_key}"
        title_label = tk.Label(
            self.main_frame,
            text=title_text,
            font=("Arial", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(pady=(0, 20))

        # Usage info
        uses_remaining = max(0, self.user_info.get('uses_remaining', 0) - 1)  # Subtract 1 to account for API delay
        uses_text = f"Uses remaining: {uses_remaining}"
        uses_label = tk.Label(
            self.main_frame,
            text=uses_text,
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        uses_label.pack(pady=(0, 20))

        # HWID info
        hwid = self.user_info.get('hwid', 'Not registered')
        hwid_text = f"Hardware ID: {hwid[:16]}..."
        hwid_label = tk.Label(
            self.main_frame,
            text=hwid_text,
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        hwid_label.pack(pady=(0, 20))

        # Main content area
        content_frame = tk.Frame(self.main_frame, bg=COLORS["background_secondary"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Example tool functionality
        tool_label = tk.Label(
            content_frame,
            text="Tool functionality goes here",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        tool_label.pack(pady=20)

        # Exit button
        exit_button = tk.Button(
            self.main_frame,
            text="Exit",
            bg=COLORS["danger"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["danger_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.exit_application
        )
        exit_button.pack(pady=20)

    def exit_application(self):
        """Exit the application"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()

    def cleanup(self):
        """Clean up temporary files"""
        try:
            if os.environ.get("TACT_CLEANUP_ON_EXIT") == "1":
                script_dir = os.environ.get("TACT_SCRIPT_DIR")
                if script_dir and os.path.exists(script_dir):
                    import shutil
                    shutil.rmtree(script_dir)
        except Exception as e:
            print(f"Cleanup error: {e}")

def main():
    try:
        root = tk.Tk()
        app = TactTool(root)
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
