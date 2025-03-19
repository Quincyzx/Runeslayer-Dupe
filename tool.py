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
from PIL import Image, ImageTk
import io
import base64
import requests
import time
import platform
import subprocess
import glob
import atexit
from auth_utils import verify_license, update_usage

# Configuration
APP_TITLE = "Tact Tool"
VERSION = "1.0"

# GitHub Configuration
GITHUB_USER = "Quincyzx"
GITHUB_REPO = "Runeslayer-Dupe"
GITHUB_BRANCH = "main"

# Modern dark theme colors with purple accent
COLORS = {
    "background": "#000000",
    "secondary_bg": "#1a1a1a",
    "accent": "#cb6ce6",
    "accent_hover": "#b44ecc",
    "text": "#ffffff",
    "text_secondary": "#858585",
    "success": "#2ecc71",
    "warning": "#f1c40f",
    "danger": "#e74c3c",
    "danger_hover": "#c0392b",
    "border": "#2a2a2a",
    "input_bg": "#1a1a1a",
}

class TactTool:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x600")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["background"])
        self.root.overrideredirect(True)

        # Variables
        self.license_key = None
        self.user_info = None

        # Setup UI
        self.setup_main_ui()

    def setup_main_ui(self):
        """Set up the main UI after authentication"""
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        content_frame = tk.Frame(self.main_frame, bg=COLORS["secondary_bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Dupe buttons container
        buttons_frame = tk.Frame(content_frame, bg=COLORS["secondary_bg"])
        buttons_frame.pack(pady=40)

        # Start Dupe button
        self.dupe_button = tk.Button(
            buttons_frame,
            text="START DUPE",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["accent"],
            fg=COLORS["text"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            padx=40,
            pady=15,
            command=self.start_dupe,
            cursor="hand2"
        )
        self.dupe_button.pack(side=tk.LEFT, padx=10)

        # End Dupe button
        self.end_dupe_button = tk.Button(
            buttons_frame,
            text="END DUPE",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["text"],
            activebackground=COLORS["danger_hover"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            padx=40,
            pady=15,
            command=self.end_dupe,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.end_dupe_button.pack(side=tk.LEFT, padx=10)

        # Status label
        self.dupe_status = tk.Label(
            content_frame,
            text="Ready to start",
            font=("Segoe UI", 12),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text_secondary"]
        )
        self.dupe_status.pack(pady=(20, 0))

    def start_dupe(self):
        """Start the duping process and disconnect from the game (Error 277)"""
        self.dupe_button.config(state=tk.DISABLED)
        self.end_dupe_button.config(state=tk.NORMAL)
        self.dupe_status.config(text="Duping in progress...", fg=COLORS["accent"])
        
        block_roblox()  # Triggers Error 277

    def end_dupe(self):
        """End the duping process and restore network"""
        self.dupe_button.config(state=tk.NORMAL)
        self.end_dupe_button.config(state=tk.DISABLED)
        self.dupe_status.config(text="Dupe ended", fg=COLORS["text_secondary"])
        
        unblock_roblox()  # Restores network

def get_roblox_path():
    """Find the latest installed RobloxPlayerBeta.exe"""
    base_path = os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions")
    versions = glob.glob(os.path.join(base_path, "*"))
    
    for version in versions:
        exe_path = os.path.join(version, "RobloxPlayerBeta.exe")
        if os.path.exists(exe_path):
            return exe_path
    return None

def block_roblox():
    """Blocks Roblox from accessing the internet to trigger error 277"""
    roblox_path = get_roblox_path()
    
    if not roblox_path:
        print("Roblox executable not found.")
        return

    if platform.system() == "Windows":
        command = f'netsh advfirewall firewall add rule name="BlockRoblox" dir=out action=block program="{roblox_path}"'
        subprocess.run(command, shell=True)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run("sudo pfctl -t roblox -T add any", shell=True)
    else:  # Linux (unlikely for Roblox)
        subprocess.run("iptables -A OUTPUT -p tcp --dport 443 -j DROP", shell=True)

    time.sleep(30)  # Wait for disconnection
    unblock_roblox()

def unblock_roblox():
    """Removes the firewall rule after disconnection"""
    roblox_path = get_roblox_path()

    if not roblox_path:
        print("Roblox executable not found.")
        return

    if platform.system() == "Windows":
        command = f'netsh advfirewall firewall delete rule name="BlockRoblox" program="{roblox_path}"'
        subprocess.run(command, shell=True)
    elif platform.system() == "Darwin":
        subprocess.run("sudo pfctl -t roblox -T delete any", shell=True)
    else:
        subprocess.run("iptables -D OUTPUT -p tcp --dport 443 -j DROP", shell=True)

def main():
    root = tk.Tk()
    app = TactTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
