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
import datetime
import tempfile
import atexit
import threading
import platform
import socket
import psutil
import random
import subprocess
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
    "background": "#000000",  # Black background
    "secondary_bg": "#1a1a1a",  # Slightly lighter black
    "accent": "#cb6ce6",  # Purple accent
    "accent_hover": "#b44ecc",  # Darker purple
    "text": "#ffffff",
    "text_secondary": "#858585",
    "success": "#2ecc71",
    "warning": "#f1c40f",
    "danger": "#e74c3c",
    "danger_hover": "#c0392b",
    "border": "#2a2a2a",
    "input_bg": "#1a1a1a",
    "tab_active": "#cb6ce6",
    "tab_inactive": "#1a1a1a",
    "tab_hover": "#252525"
}

def get_logo_from_github():
    """Fetch the banner from GitHub and return as PhotoImage"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/Tactbanner"
        headers = {
            "Authorization": f"token {os.environ.get('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = base64.b64decode(response.json()['content'])
            image = Image.open(io.BytesIO(content))
            # Adjust size to maintain aspect ratio while fitting width
            aspect_ratio = image.width / image.height
            new_width = 800
            new_height = int(new_width / aspect_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading banner: {e}")
    return None

class TactTool:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("900x600")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["background"])
        self.root.overrideredirect(True)  # Remove default window decorations
        
        # Custom title bar
        title_bar = tk.Frame(self.root, bg=COLORS["background"], height=30)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        title_bar.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            title_bar,
            text=APP_TITLE,
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Segoe UI", 10)
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Minimize and close buttons
        close_button = tk.Button(
            title_bar,
            text="✕",
            bg=COLORS["background"],
            fg=COLORS["text"],
            bd=0,
            font=("Segoe UI", 10),
            width=3,
            command=self.root.quit
        )
        close_button.pack(side=tk.RIGHT)
        
        minimize_button = tk.Button(
            title_bar,
            text="−",
            bg=COLORS["background"],
            fg=COLORS["text"],
            bd=0,
            font=("Segoe UI", 10),
            width=3,
            command=self.root.iconify
        )
        minimize_button.pack(side=tk.RIGHT)
        
        # Bind dragging events
        title_bar.bind("<Button-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.on_move)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)

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
        self.dupe_active = False
        self.dupe_thread = None
        self.status_thread = None
        self.firewall_rule_name = "TactToolRobloxBlock"

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

        # Logo for login screen
        try:
            url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/Tact.png"
            headers = {
                "Authorization": f"token {os.environ.get('GITHUB_TOKEN')}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                content = base64.b64decode(response.json()['content'])
                image = Image.open(io.BytesIO(content))
                # Resize image to match desired size
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(image)
                logo_label = tk.Label(
                    self.auth_frame,
                    image=self.logo_image,
                    bg=COLORS["background"]
                )
                logo_label.pack(pady=(0, 50))
        except Exception as e:
            print(f"Error loading logo: {e}")
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
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create tab buttons frame at the very top
        self.tab_buttons = tk.Frame(self.main_frame, bg=COLORS["background"])
        self.tab_buttons.pack(fill=tk.X, padx=10, pady=5)

        # Add banner below tab buttons with transparent background
        banner_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        banner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Get and display banner
        try:
            url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/Tactbanner"
            headers = {
                "Authorization": f"token {os.environ.get('GITHUB_TOKEN')}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                content = base64.b64decode(response.json()['content'])
                image = Image.open(io.BytesIO(content))
                # Adjust size to maintain aspect ratio while fitting width
                aspect_ratio = image.width / image.height
                new_width = 300  # Even smaller banner width
                new_height = int(new_width / aspect_ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.banner = ImageTk.PhotoImage(image)
                banner_label = tk.Label(
                    banner_frame,
                    image=self.banner,
                    bg=COLORS["background"]
                )
                banner_label.pack(fill=tk.X)
        except Exception as e:
            print(f"Error loading banner: {e}")

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
        self.create_info_row(info_frame, "Hardware ID", hwid, 2)

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

        # Container for dupe buttons
        dupe_frame = tk.Frame(main_frame, bg=COLORS["secondary_bg"], padx=20, pady=20)
        dupe_frame.pack(fill=tk.X)

        # Dupe status
        self.dupe_status = tk.Label(
            dupe_frame,
            text="Ready",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text_secondary"]
        )
        self.dupe_status.pack(pady=(0, 20))

        # Button frame
        button_frame = tk.Frame(dupe_frame, bg=COLORS["secondary_bg"])
        button_frame.pack()

        # Dupe button
        self.dupe_button = tk.Button(
            button_frame,
            text="DUPE",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["accent"],
            fg=COLORS["text"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            padx=40,
            pady=15,
            command=self.start_dupe
        )
        self.dupe_button.pack(side=tk.LEFT, padx=10)

        # End dupe button (disabled by default)
        self.end_dupe_button = tk.Button(
            button_frame,
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
            state=tk.DISABLED
        )
        self.end_dupe_button.pack(side=tk.LEFT, padx=10)

    def get_roblox_ips(self):
        """Get all active Roblox IP addresses"""
        roblox_ips = []
        try:
            # Find all Roblox processes
            roblox_processes = []
            for process in psutil.process_iter(['pid', 'name']):
                if process.info['name'] and "Roblox" in process.info['name']:
                    roblox_processes.append(process.info['pid'])
            
            # Get all connections from Roblox processes
            for pid in roblox_processes:
                try:
                    process = psutil.Process(pid)
                    connections = process.connections(kind='inet')
                    for conn in connections:
                        if conn.status == 'ESTABLISHED' and conn.raddr:
                            remote_ip = conn.raddr.ip
                            if remote_ip not in roblox_ips:
                                roblox_ips.append(remote_ip)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error getting Roblox IPs: {e}")
        
        return roblox_ips

    def block_roblox_ips(self, ips):
        """Block Roblox IPs using Windows Firewall"""
        if platform.system() != "Windows":
            return False, "Firewall blocking only works on Windows"
        
        try:
            # First, remove any existing rules with the same name
            self.remove_firewall_rules()
            
            # Block the entire Roblox subnet - this is more effective than individual IPs
            # Create outbound block rule
            cmd_out = f'netsh advfirewall firewall add rule name="{self.firewall_rule_name}" dir=out action=block remoteip=128.116.0.0/16'
            subprocess.run(cmd_out, shell=True, check=True)
            
            # Create inbound block rule
            cmd_in = f'netsh advfirewall firewall add rule name="{self.firewall_rule_name}" dir=in action=block remoteip=128.116.0.0/16'
            subprocess.run(cmd_in, shell=True, check=True)
            
            return True, "Blocked Roblox subnet"
        except Exception as e:
            print(f"Error blocking IPs: {e}")
            return False, f"Error blocking IPs: {str(e)}"

    def remove_firewall_rules(self):
        """Remove all firewall rules created by this tool"""
        if platform.system() != "Windows":
            return
        
        try:
            cmd = f'netsh advfirewall firewall delete rule name="{self.firewall_rule_name}"'
            subprocess.run(cmd, shell=True)
        except Exception as e:
            print(f"Error removing firewall rules: {e}")

    def start_dupe(self):
        """Start the duping process by blocking Roblox IPs"""
        # Check if already duping
        if self.dupe_active:
            return
            
        # Disable the dupe button and enable end button
        self.dupe_button.config(state=tk.DISABLED)
        self.end_dupe_button.config(state=tk.NORMAL)
        self.dupe_status.config(text="Active", fg=COLORS["accent"])
        
        # Set flag to indicate duping is active
        self.dupe_active = True
        
        # Function to block Roblox IPs
        def block_roblox_connection():
            try:
                # Check if running on Windows
                if platform.system() != "Windows":
                    print("IP blocking is only supported on Windows")
                    self.root.after(0, lambda: self.dupe_status.config(
                        text="Windows required", 
                        fg=COLORS["warning"]
                    ))
                    return
                
                # Get Roblox IPs
                roblox_ips = self.get_roblox_ips()
                
                if not roblox_ips:
                    print("No Roblox IPs found")
                    self.root.after(0, lambda: self.dupe_status.config(
                        text="No Roblox connections", 
                        fg=COLORS["warning"]
                    ))
                    return
                
                print(f"Found {len(roblox_ips)} Roblox IPs: {roblox_ips}")
                
                # Block the IPs
                success, message = self.block_roblox_ips(roblox_ips)
                
                if success:
                    print(f"Successfully blocked Roblox IPs: {message}")
                else:
                    print(f"Failed to block Roblox IPs: {message}")
                    self.root.after(0, lambda: self.dupe_status.config(
                        text=message, 
                        fg=COLORS["warning"]
                    ))
                
                # Keep the thread alive while duping is active
                while self.dupe_active:
                    time.sleep(0.5)
                    
                # Clean up when duping ends
                self.remove_firewall_rules()
                
            except Exception as e:
                print(f"Error in dupe thread: {e}")
                self.root.after(0, lambda: self.dupe_status.config(
                    text=f"Error: {str(e)}", 
                    fg=COLORS["danger"]
                ))
            finally:
                print("Dupe thread stopped")
        
        # Start thread to handle IP blocking
        self.dupe_thread = threading.Thread(target=block_roblox_connection)
        self.dupe_thread.daemon = True
        self.dupe_thread.start()

    def end_dupe(self):
        """End the duping process"""
        # Stop the dupe process
        self.dupe_active = False
        
        # If there's a thread, wait for it to end
        if self.dupe_thread and self.dupe_thread.is_alive():
            try:
                self.dupe_thread.join(timeout=1.0)
            except:
                pass
        
        # Make sure all firewall rules are removed
        self.remove_firewall_rules()
        
        # Update UI
        self.dupe_button.config(state=tk.NORMAL)
        self.end_dupe_button.config(state=tk.DISABLED)
        self.dupe_status.config(text="Ready", fg=COLORS["text_secondary"])

    def exit_application(self):
        """Exit the application"""
        # Stop the dupe process if it's running
        if self.dupe_active:
            self.end_dupe()
        
        # Remove any remaining firewall rules
        self.remove_firewall_rules()
        
        self.root.quit()

    def start_move(self, event):
        """Start window movement"""
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        """Handle window movement"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def cleanup(self):
        """Clean up temporary files and remove firewall rules"""
        # Make sure all firewall rules are removed
        self.remove_firewall_rules()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = TactTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
