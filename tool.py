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

# Modern dark theme colors - Roblox executor inspired
COLORS = {
    "background": "#121212",  # Darker background
    "secondary_bg": "#1e1e1e",  # Slightly lighter background
    "accent": "#00b4ff",  # Bright cyan accent
    "accent_hover": "#0095d9",
    "text": "#ffffff",
    "text_secondary": "#858585",
    "success": "#2ecc71",
    "warning": "#f1c40f",
    "danger": "#e74c3c",
    "danger_hover": "#c0392b",
    "border": "#2a2a2a",
    "input_bg": "#1a1a1a",
    "tab_active": "#00b4ff",
    "tab_inactive": "#1a1a1a",
    "tab_hover": "#252525"
}

class TactTool:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x600")
        self.root.minsize(900, 600)
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

        # Configure ttk styles
        self.setup_styles()

        # Set up authentication UI
        self.setup_auth_ui()

        # Register cleanup
        if os.environ.get("TACT_CLEANUP_ON_EXIT") == "1":
            atexit.register(self.cleanup)

    def setup_styles(self):
        """Set up custom ttk styles"""
        style = ttk.Style()

        # Configure frames
        style.configure(
            "Custom.TFrame",
            background=COLORS["background"]
        )

    def setup_auth_ui(self):
        """Set up the authentication UI"""
        # Main container
        self.auth_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.auth_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400)

        # Title
        title_label = tk.Label(
            self.auth_frame,
            text="Tact Tool",
            font=("Segoe UI", 32, "bold"),
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack(pady=(0, 30))

        # License key entry frame
        key_frame = tk.Frame(self.auth_frame, bg=COLORS["background"])
        key_frame.pack(pady=(0, 20), fill=tk.X)

        # License key label
        key_label = tk.Label(
            key_frame,
            text="License Key",
            font=("Segoe UI", 12),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        key_label.pack(anchor=tk.W, padx=(0, 10), pady=(0, 5))

        # Key entry with modern styling
        self.key_entry = tk.Entry(
            key_frame,
            font=("Segoe UI", 12),
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            width=30
        )
        self.key_entry.pack(fill=tk.X, ipady=10)

        # Add a border effect
        border_frame = tk.Frame(key_frame, bg=COLORS["accent"], height=2)
        border_frame.pack(fill=tk.X, pady=(0, 5))

        # Login button with hover effect
        self.login_button = tk.Button(
            self.auth_frame,
            text="LOGIN",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["accent"],
            fg=COLORS["text"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            padx=40,
            pady=12,
            command=self.login,
            cursor="hand2"  # Hand cursor on hover
        )
        self.login_button.pack(pady=(20, 30))

        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Enter your license key to continue")

        status_label = tk.Label(
            self.auth_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg=COLORS["background"],
            fg=COLORS["text_secondary"],
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
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create tab buttons frame
        self.tab_buttons = tk.Frame(self.main_frame, bg=COLORS["background"])
        self.tab_buttons.pack(fill=tk.X, padx=10, pady=(0, 20))

        # Create content frame
        self.content_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Create tab buttons
        self.current_tab = tk.StringVar(value="profile")

        profile_btn = tk.Button(
            self.tab_buttons,
            text="Profile",
            font=("Segoe UI", 11),
            bg=COLORS["accent"] if self.current_tab.get() == "profile" else COLORS["tab_inactive"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            padx=30,
            pady=12,
            command=lambda: self.switch_tab("profile"),
            cursor="hand2"
        )
        profile_btn.pack(side=tk.LEFT, padx=5)

        main_btn = tk.Button(
            self.tab_buttons,
            text="Main",
            font=("Segoe UI", 11),
            bg=COLORS["tab_inactive"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            padx=30,
            pady=12,
            command=lambda: self.switch_tab("main"),
            cursor="hand2"
        )
        main_btn.pack(side=tk.LEFT, padx=5)

        # Store buttons for later reference
        self.tab_buttons_dict = {
            "profile": profile_btn,
            "main": main_btn
        }

        # Create tab frames
        self.profile_tab = tk.Frame(self.content_frame, bg=COLORS["background"])
        self.main_tab = tk.Frame(self.content_frame, bg=COLORS["background"])

        # Set up initial tab
        self.setup_profile_tab()
        self.setup_main_tab()
        self.switch_tab("profile")

    def switch_tab(self, tab_name):
        """Switch between tabs"""
        # Update button colors
        for name, button in self.tab_buttons_dict.items():
            button.configure(bg=COLORS["accent"] if name == tab_name else COLORS["tab_inactive"])

        # Update current tab
        self.current_tab.set(tab_name)

        # Hide all tabs
        self.profile_tab.pack_forget()
        self.main_tab.pack_forget()

        # Show selected tab
        if tab_name == "profile":
            self.profile_tab.pack(fill=tk.BOTH, expand=True)
        else:
            self.main_tab.pack(fill=tk.BOTH, expand=True)

    def setup_profile_tab(self):
        """Set up the profile tab content"""
        # Profile container
        profile_frame = tk.Frame(self.profile_tab, bg=COLORS["background"])
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Title
        title_label = tk.Label(
            profile_frame,
            text="User Profile",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack(anchor=tk.W, pady=(0, 30))

        # User info container
        info_frame = tk.Frame(profile_frame, bg=COLORS["secondary_bg"])
        info_frame.pack(fill=tk.X, pady=(0, 20), ipady=20)

        # License Key info
        self.create_info_row(info_frame, "License Key", self.license_key, 0)

        # Uses info
        uses_remaining = max(0, self.user_info.get('uses_remaining', 0) - 1)
        self.create_info_row(info_frame, "Uses Remaining", str(uses_remaining), 1)

        # HWID info
        hwid = self.user_info.get('hwid', 'Not registered')
        self.create_info_row(info_frame, "Hardware ID", hwid[:16] + "...", 2)

    def create_info_row(self, parent, label, value, row):
        """Create a row of information in the profile tab"""
        # Label
        tk.Label(
            parent,
            text=label,
            font=("Segoe UI", 12),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text_secondary"]
        ).grid(row=row, column=0, padx=20, pady=10, sticky=tk.W)

        # Value
        tk.Label(
            parent,
            text=value,
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        ).grid(row=row, column=1, padx=20, pady=10, sticky=tk.W)

    def setup_main_tab(self):
        """Set up the main tab content"""
        main_frame = tk.Frame(self.main_tab, bg=COLORS["background"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Main Dashboard",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack(anchor=tk.W, pady=(0, 30))

        # Content area
        content_frame = tk.Frame(main_frame, bg=COLORS["secondary_bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Example tool functionality
        tool_label = tk.Label(
            content_frame,
            text="Tool functionality goes here",
            font=("Segoe UI", 14),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        tool_label.pack(pady=40)

        # Exit button at the bottom
        exit_button = tk.Button(
            self.main_frame,
            text="EXIT",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["text"],
            activebackground=COLORS["danger_hover"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.exit_application
        )
        exit_button.pack(side=tk.BOTTOM, pady=20)

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
