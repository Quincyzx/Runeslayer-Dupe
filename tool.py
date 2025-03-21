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
        self.proxy_process = None

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

    def create_proxy_script(self):
        """Create a temporary Python script that will act as a network proxy to drop Roblox packets"""
        # Create a temp file for the script
        fd, script_path = tempfile.mkstemp(suffix='.py')
        os.close(fd)
        
        # Write the proxy script
        proxy_code = """
import socket
import threading
import time
import random

# Roblox IP ranges to target
ROBLOX_IPS = [
    '128.116.0.0/16',  # Main Roblox subnet
]

def ip_in_subnet(ip, subnet):
    '''Check if an IP is in a subnet'''
    ip_parts = list(map(int, ip.split('.')))
    subnet_parts = subnet.split('/')
    subnet_ip = list(map(int, subnet_parts[0].split('.')))
    subnet_mask = int(subnet_parts[1])
    
    # Convert IPs to integers
    ip_int = (ip_parts[0] << 24) + (ip_parts[1] << 16) + (ip_parts[2] << 8) + ip_parts[3]
    subnet_int = (subnet_ip[0] << 24) + (subnet_ip[1] << 16) + (subnet_ip[2] << 8) + subnet_ip[3]
    
    # Create mask
    mask = ((1 << 32) - 1) ^ ((1 << (32 - subnet_mask)) - 1)
    
    return (ip_int & mask) == (subnet_int & mask)

def is_roblox_ip(ip):
    '''Check if an IP belongs to Roblox'''
    for subnet in ROBLOX_IPS:
        if ip_in_subnet(ip, subnet):
            return True
    return False

def handle_udp_forward(src_data, src_addr, dst_socket, dst_addr, direction):
    '''Handle UDP packet forwarding with packet dropping for Roblox servers'''
    # Check if this is traffic to a Roblox server
    if direction == "outbound" and is_roblox_ip(dst_addr[0]):
        # Randomly drop packets (90% drop rate)
        if random.random() < 0.9:
            print(f"Dropping packet to Roblox: {dst_addr}")
            return
    
    try:
        dst_socket.sendto(src_data, dst_addr)
    except Exception as e:
        print(f"Forward error: {e}")

def udp_proxy(local_port):
    '''Create a UDP proxy that forwards packets except to Roblox servers'''
    try:
        # Create local UDP socket to receive data
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        local_socket.bind(('127.0.0.1', local_port))
        
        # Socket to forward data
        forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Connection tracking for return packets
        connections = {}
        
        print(f"UDP proxy started on port {local_port}")
        
        while True:
            try:
                # Receive data from client
                data, addr = local_socket.recvfrom(4096)
                
                if addr in connections:
                    # This is a response packet
                    original_dst = connections[addr]
                    handle_udp_forward(data, addr, forward_socket, original_dst, "inbound")
                else:
                    # This is a new outbound connection
                    # Modify the packet if it's going to a Roblox server
                    handle_udp_forward(data, addr, forward_socket, (addr[0], addr[1]), "outbound")
                    
                    # Track this connection for responses
                    connections[addr] = (addr[0], addr[1])
            except Exception as e:
                print(f"Proxy error: {e}")
                continue
    
    except Exception as e:
        print(f"UDP proxy error: {e}")
        
    finally:
        try:
            local_socket.close()
            forward_socket.close()
        except:
            pass

if __name__ == "__main__":
    # Start the proxy on all Roblox ports
    proxy_port = 8591  # Local proxy port
    
    proxy_thread = threading.Thread(target=udp_proxy, args=(proxy_port,))
    proxy_thread.daemon = True
    proxy_thread.start()
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Proxy shutting down...")
        """
        
        with open(script_path, 'w') as f:
            f.write(proxy_code)
            
        return script_path

    def start_dupe(self):
        """Start the duping process using UDP packet interception"""
        # Check if already duping
        if self.dupe_active:
            return
            
        # Disable the dupe button and enable end button
        self.dupe_button.config(state=tk.DISABLED)
        self.end_dupe_button.config(state=tk.NORMAL)
        self.dupe_status.config(text="Active", fg=COLORS["accent"])
        
        # Set flag to indicate duping is active
        self.dupe_active = True
        
        # Function to trigger Error 277 via packet dropping
        def run_packet_dropper():
            try:
                # Create the proxy script
                script_path = self.create_proxy_script()
                
                # Start the proxy in a separate process
                self.proxy_process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                print(f"Started packet dropper: {script_path}")
                
                # Monitor the process
                while self.dupe_active:
                    # Check if process is still running
                    if self.proxy_process.poll() is not None:
                        # Process exited
                        stdout, stderr = self.proxy_process.communicate()
                        print(f"Packet dropper exited. Output: {stdout}")
                        print(f"Errors: {stderr}")
                        self.root.after(0, lambda: self.dupe_status.config(
                            text="Proxy error", 
                            fg=COLORS["warning"]
                        ))
                        break
                        
                    # Wait a bit
                    time.sleep(0.5)
                
                # Clean up
                self.cleanup_proxy()
                
            except Exception as e:
                print(f"Error in dupe thread: {e}")
                self.root.after(0, lambda: self.dupe_status.config(
                    text=f"Error: {str(e)}", 
                    fg=COLORS["danger"]
                ))
            finally:
                print("Dupe thread stopped")
        
        # Start thread to handle the duping
        self.dupe_thread = threading.Thread(target=run_packet_dropper)
        self.dupe_thread.daemon = True
        self.dupe_thread.start()

    def cleanup_proxy(self):
        """Terminate the proxy process and clean up"""
        if self.proxy_process:
            try:
                # Try to terminate gracefully
                self.proxy_process.terminate()
                self.proxy_process.wait(timeout=2)
            except:
                # Force kill if it doesn't terminate gracefully
                try:
                    self.proxy_process.kill()
                except:
                    pass
            
            self.proxy_process = None

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
        
        # Clean up proxy
        self.cleanup_proxy()
        
        # Update UI
        self.dupe_button.config(state=tk.NORMAL)
        self.end_dupe_button.config(state=tk.DISABLED)
        self.dupe_status.config(text="Ready", fg=COLORS["text_secondary"])

    def exit_application(self):
        """Exit the application"""
        # Stop the dupe process if it's running
        if self.dupe_active:
            self.end_dupe()
        
        # Final cleanup
        self.cleanup_proxy()
        
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
        """Clean up resources"""
        # Clean up proxy
        self.cleanup_proxy()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = TactTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
