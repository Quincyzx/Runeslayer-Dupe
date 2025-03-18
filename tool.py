#!/usr/bin/env python3
"""
RuneSlayer Tool - Main Application
This file handles authentication and provides the main tool functionality.
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
from pathlib import Path

# GitHub Configuration
GITHUB_USER = "Quincyzx"        # GitHub username 
GITHUB_REPO = "Runeslayer-Dupe" # GitHub repository name
GITHUB_BRANCH = "master"        # GitHub branch name
KEYS_FILE_PATH = "keys.json"    # Path to keys file in GitHub repo

# Hardcoded GitHub token (will encrypt later)
GITHUB_TOKEN = "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"

# Print token status for debugging (don't print the token itself)
print(f"Tool.py - GitHub Token available: {bool(GITHUB_TOKEN)}")
print(f"Tool.py - Current environment variables: {list(os.environ.keys())}")

# Debug output for GitHub token
print(f"Tool.py - GitHub Token available: {bool(GITHUB_TOKEN)}")
print(f"Tool.py - Current environment variables: {list(os.environ.keys())}")

# Cooldown configuration
COOLDOWN_MINUTES = 6  # 6 minute cooldown period

def get_system_id():
    """Get a unique system identifier based on hardware"""
    # Get hardware info that's difficult to change
    hw_info = f"{platform.node()}:{platform.machine()}:{str(uuid.getnode())}"
    # Create a hash of the hardware info
    return hashlib.sha256(hw_info.encode()).hexdigest()

def get_cooldown_file_path():
    """Get the path to the hidden cooldown file"""
    system_id = get_system_id()
    
    # Determine OS type to find appropriate hidden location
    if platform.system() == 'Windows':
        # On Windows, use AppData\Local\Microsoft\Crypto folder (rarely accessed by users)
        base_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Crypto')
        if not os.path.exists(base_dir):
            # Fallback to a different hidden location
            base_dir = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Internet Explorer', 'Recovery')
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
        
        # Create a hidden filename that looks like system file
        filename = f"MS{system_id[:8]}.dat"
        
    elif platform.system() == 'Darwin':  # macOS
        # On macOS, use Library/Application Support/com.apple.TCC
        base_dir = os.path.expanduser('~/Library/Application Support/com.apple.TCC')
        if not os.path.exists(base_dir):
            base_dir = os.path.expanduser('~/Library/Caches/com.apple.AppleDB')
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
        
        # Create a hidden filename with dot prefix
        filename = f".apple_db_{system_id[:8]}.plist"
        
    else:  # Linux and others
        # On Linux, use .config/dconf folder
        base_dir = os.path.expanduser('~/.config/dconf')
        if not os.path.exists(base_dir):
            base_dir = os.path.expanduser('~/.local/share/system-cache')
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
        
        # Create a hidden filename with dot prefix
        filename = f".system_{system_id[:8]}.cache"
    
    # Return the full path
    return os.path.join(base_dir, filename)

def is_on_cooldown():
    """Check if the application is on cooldown"""
    cooldown_file = get_cooldown_file_path()
    
    try:
        # Check if cooldown file exists
        if os.path.exists(cooldown_file):
            # Read the last usage timestamp from file
            with open(cooldown_file, 'r') as f:
                try:
                    content = f.read().strip()
                    # Parse the timestamp
                    parts = content.split('|')
                    if len(parts) >= 2:
                        last_used_str = parts[1]
                        last_used = float(last_used_str)
                        
                        # Calculate time elapsed since last usage
                        current_time = time.time()
                        elapsed_minutes = (current_time - last_used) / 60
                        
                        print(f"Last usage was {elapsed_minutes:.2f} minutes ago")
                        
                        # Check if we're still in cooldown period
                        if elapsed_minutes < COOLDOWN_MINUTES:
                            remaining_minutes = COOLDOWN_MINUTES - elapsed_minutes
                            return True, remaining_minutes
                except Exception as e:
                    print(f"Error parsing cooldown file: {str(e)}")
                    # If we can't parse the file, assume no cooldown
    except Exception as e:
        print(f"Error checking cooldown: {str(e)}")
    
    # If we reach here, no cooldown is active
    return False, 0

def update_cooldown_file():
    """Update the cooldown file with the current usage time"""
    cooldown_file = get_cooldown_file_path()
    
    try:
        # Create or update the cooldown file
        system_id = get_system_id()
        current_time = time.time()
        
        # Format: system_id|timestamp
        content = f"{system_id}|{current_time}"
        
        # Write to the file
        with open(cooldown_file, 'w') as f:
            f.write(content)
        
        # On Windows, try to make the file hidden
        if platform.system() == 'Windows':
            try:
                subprocess.run(['attrib', '+h', cooldown_file], check=False)
            except:
                pass
        
        print(f"Cooldown file updated at {cooldown_file}")
        return True
    except Exception as e:
        print(f"Error updating cooldown file: {str(e)}")
        return False

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
    "border": "#42454A",
    "input_bg": "#40444B"
}

class RuneSlayerTool:
    def __init__(self, root, user_info=None):
        self.root = root
        self.root.title("RuneSlayer")
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        self.root.configure(bg=COLORS["background"])
        
        # User info received from authentication
        self.user_info = user_info
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Setup main UI - blank page with welcome message
        self.setup_blank_ui()
    
    def setup_blank_ui(self):
        """Set up a blank UI with just a welcome message"""
        # Main container
        main_frame = tk.Frame(self.root, bg=COLORS["background"])
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Welcome to RuneSlayer",
            font=("Arial", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(pady=(0, 20))
        
        # Authentication success message
        auth_message = tk.Label(
            main_frame,
            text="Authentication Successful!",
            font=("Arial", 16),
            bg=COLORS["background"],
            fg=COLORS["success"]
        )
        auth_message.pack(pady=(0, 30))
        
        # User info display
        if self.user_info:
            # Format user info for display
            key = self.user_info.get('key', 'Unknown')
            uses = self.user_info.get('uses_remaining', 0)
            hwid = self.user_info.get('hwid', 'Unknown')
            
            # Truncate key and hwid for display
            display_key = key[:10] + "..." + key[-5:] if len(key) > 15 else key
            display_hwid = hwid[:10] + "..." if len(hwid) > 10 else hwid
            
            info_text = f"License: {display_key}\nUses Remaining: {uses}\nHWID: {display_hwid}"
            
            user_info_label = tk.Label(
                main_frame,
                text=info_text,
                bg=COLORS["background"],
                fg=COLORS["text"],
                justify=tk.LEFT
            )
            user_info_label.pack(pady=10)


class AuthenticationApp:
    """Authentication window for RuneSlayer"""
    def __init__(self, root):
        self.root = root
        self.root.title("RuneSlayer Authentication")
        self.root.geometry("500x300")
        self.root.minsize(500, 300)
        self.root.configure(bg=COLORS["background"])
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Variables
        self.auth_thread = None
        self.authenticated = False
        self.user_info = None
        
        # Setup UI
        self.setup_login_ui()
    
    def setup_login_ui(self):
        """Set up the login UI"""
        # Main container
        self.login_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(
            self.login_frame,
            text="RuneSlayer",
            font=("Arial", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(pady=(0, 20))
        
        # Login container
        login_container = tk.Frame(self.login_frame, bg=COLORS["background_secondary"], padx=30, pady=30)
        login_container.pack()
        
        # Key input
        key_label = tk.Label(
            login_container,
            text="License Key",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        key_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.key_var = tk.StringVar()
        
        key_entry = tk.Entry(
            login_container,
            textvariable=self.key_var,
            width=35,
            bg=COLORS["input_bg"],
            fg=COLORS["text_bright"],
            insertbackground=COLORS["text_bright"],
            relief=tk.FLAT,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        key_entry.pack(pady=(0, 15))
        
        # Login button
        self.login_button = tk.Button(
            login_container,
            text="Authenticate",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.authenticate
        )
        self.login_button.pack(pady=(10, 0))
        
        # Status message
        self.login_status_var = tk.StringVar()
        self.login_status_label = tk.Label(
            login_container,
            textvariable=self.login_status_var,
            bg=COLORS["background_secondary"],
            fg=COLORS["danger"],
            wraplength=300
        )
        self.login_status_label.pack(pady=(15, 0))
    
    def authenticate(self):
        """Authenticate user with license key"""
        license_key = self.key_var.get().strip()
        
        if not license_key:
            self.login_status_var.set("Please enter a license key")
            return
        
        # Show loading message
        self.login_status_var.set("Authenticating...")
        self.login_button.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            # Create authentication thread
            self.auth_thread = threading.Thread(target=self._authenticate_thread, args=(license_key,))
            self.auth_thread.daemon = True
            self.auth_thread.start()
        except Exception as e:
            self.login_status_var.set(f"Authentication error: {str(e)}")
            self.login_button.config(state=tk.NORMAL)
    
    def get_sha_of_file(self):
        """Get the SHA of the keys file on GitHub (required for updating)"""
        api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{KEYS_FILE_PATH}"
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            print(f"Getting SHA from: {api_url}")
            response = requests.get(api_url, headers=headers)
            print(f"SHA response status: {response.status_code}")
            
            if response.status_code == 200:
                file_data = response.json()
                sha = file_data.get('sha')
                if sha:
                    print(f"SHA found: {sha}")
                    return sha
                else:
                    print(f"SHA not found in response: {file_data}")
                    return None
            else:
                print(f"Error getting file info: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Exception getting SHA: {str(e)}")
            return None
    
    def update_keys_on_github(self, keys_data, sha):
        """Update the keys file on GitHub after using a key"""
        api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{KEYS_FILE_PATH}"
        
        # Prepare the content for the file
        content = json.dumps(keys_data, indent=4)
        
        # GitHub API requires Base64 encoded content
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        # For public repositories, we still need a token to push changes
        # This will only work if you have write access to the repository
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Add token if available
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
            print("Using GitHub token for authentication when updating keys")
        else:
            print("Warning: No GitHub token available for updating keys")
        
        data = {
            "message": "Update keys after authentication",
            "content": encoded_content,
            "sha": sha  # Use the retrieved SHA for the update
        }
        
        try:
            print(f"Updating keys at: {api_url}")
            response = requests.put(api_url, json=data, headers=headers)
            print(f"Update response status: {response.status_code}")
            
            if response.status_code in (200, 201):
                print("Successfully updated keys.json on GitHub.")
                return True
            else:
                print(f"Error updating keys.json on GitHub: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Exception updating keys: {str(e)}")
            return False
    
    def download_file_from_github(self, file_path):
        """Download a file from GitHub using raw URL for public repositories"""
        # Construct raw GitHub URL
        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{file_path}"
        print(f"Downloading file from GitHub: {file_path}")
        print(f"Raw URL: {url}")
        
        try:
            # Make the request
            print(f"Making request to GitHub raw URL...")
            response = requests.get(url)
            print(f"Response status code: {response.status_code}")
            
            # Check for successful response
            if response.status_code == 200:
                print("GitHub download successful")
                content = response.content
                print(f"Successfully downloaded content (length: {len(content)} bytes)")
                
                # Return content as string
                return True, content.decode('utf-8')
            else:
                # Handle error response
                error_message = f"Failed to download file. Status code: {response.status_code}"
                print(f"Download error: {error_message}")
                return False, error_message
        
        except Exception as e:
            # Handle exceptions
            return False, f"An error occurred: {str(e)}"
    
    def _authenticate_thread(self, license_key):
        """Authentication process in a separate thread"""
        try:
            # Debug output
            print(f"Starting authentication with key: {license_key}")
            
            # Download keys.json from GitHub
            success, result = self.download_file_from_github(KEYS_FILE_PATH)
            
            if success:
                # Parse the JSON data
                keys_data = json.loads(result)
                
                # Check if key is valid
                valid_key = False
                key_info = None
                key_index = -1
                
                # Print all available keys for debugging
                print("Available keys in the database:")
                for idx, key_entry in enumerate(keys_data.get("keys", [])):
                    print(f"  Key {idx+1}: {key_entry.get('key')} (Uses remaining: {key_entry.get('uses_remaining', 0)})")
                    
                    if key_entry.get("key") == license_key:
                        print(f"Found matching key: {license_key}")
                        # Check uses remaining
                        uses_remaining = key_entry.get("uses_remaining", 0)
                        print(f"Uses remaining: {uses_remaining}")
                        if uses_remaining > 0:
                            valid_key = True
                            key_info = key_entry
                            key_index = idx
                            print("Key is valid with uses remaining!")
                            break
                        else:
                            print("Key has no uses remaining")
                            self.root.after(0, lambda: self._update_auth_status(False, "License key has no uses remaining"))
                            return
                
                if valid_key:
                    # Get current HWID
                    current_hwid = str(uuid.getnode())  # MAC address as HWID
                    
                    # Check if HWID is already set and matches (first ensure key_info is not None)
                    if key_info is not None:
                        stored_hwid = key_info.get("hwid")
                        if stored_hwid and stored_hwid != current_hwid:
                            print(f"HWID mismatch: stored {stored_hwid}, current {current_hwid}")
                            self.root.after(0, lambda: self._update_auth_status(False, "HWID mismatch! License is bound to another system."))
                            return
                    
                    # Authentication successful - continue
                    # Make sure key_info is not None
                    uses_remaining = 0
                    if key_info is not None:
                        uses_remaining = key_info.get("uses_remaining", 0)
                    
                    # Decrement the uses for the key
                    updated_uses = uses_remaining - 1
                    print(f"Decrementing uses from {uses_remaining} to {updated_uses}")
                    
                    self.user_info = {
                        "key": license_key,
                        "uses_remaining": updated_uses,
                        "hwid": current_hwid
                    }
                    
                    # Update the key in GitHub if possible
                    sha = self.get_sha_of_file()
                    if sha:
                        # Update the key data in the original JSON
                        # Make sure we're updating the right key by checking again
                        for idx, key_entry in enumerate(keys_data.get("keys", [])):
                            if key_entry.get("key") == license_key:
                                print(f"Updating key at index {idx}")
                                # Decrement the uses_remaining value
                                keys_data["keys"][idx]["uses_remaining"] = updated_uses
                                # Set the HWID if not already set
                                if not keys_data["keys"][idx].get("hwid"):
                                    keys_data["keys"][idx]["hwid"] = current_hwid
                                    print(f"Setting HWID for key: {current_hwid}")
                                break
                        
                        # Update the file on GitHub
                        update_success = self.update_keys_on_github(keys_data, sha)
                        print(f"GitHub update success: {update_success}")
                        
                        if not update_success:
                            print("Failed to update key uses on GitHub")
                    else:
                        print("Failed to get SHA for GitHub update")
                    
                    # Return successful authentication
                    self.root.after(0, lambda: self._update_auth_status(True, f"Authentication successful! Uses remaining: {updated_uses}"))
                    return
                else:
                    # Invalid key
                    self.root.after(0, lambda: self._update_auth_status(False, "Invalid license key"))
                    return
            else:
                # Failed to download keys file
                error_msg = result if isinstance(result, str) else "Failed to access license database"
                self.root.after(0, lambda: self._update_auth_status(False, f"Authentication error: {error_msg}"))
                return
            
        except Exception as e:
            self.root.after(0, lambda: self._update_auth_status(False, f"Authentication error: {str(e)}"))
    
    def _update_auth_status(self, success, message):
        """Update authentication status on the main thread"""
        if success:
            self.login_status_label.config(fg=COLORS["success"])
            self.login_status_var.set(message)
            self.authenticated = True
            
            # Update the cooldown file to start the cooldown timer
            print("Authentication successful, updating cooldown file")
            update_cooldown_file()
            
            # Wait a moment then start the main application
            self.root.after(1500, self.start_main_application)
        else:
            self.login_status_label.config(fg=COLORS["danger"])
            self.login_status_var.set(message)
            self.login_button.config(state=tk.NORMAL)
    
    def start_main_application(self):
        """Start the main application after successful authentication"""
        # Destroy the login window
        self.login_frame.destroy()
        
        # Create and show the main application
        main_app = RuneSlayerTool(self.root, self.user_info)

# Secure cleanup functions
def secure_delete_file(file_path):
    """Securely delete a file by overwriting it with random data before deleting"""
    if not os.path.exists(file_path):
        return
    
    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Open file for binary write
        with open(file_path, "wb") as f:
            # First pass: Overwrite with zeros
            f.write(b'\x00' * file_size)
            f.flush()
            os.fsync(f.fileno())
            
            # Second pass: Overwrite with ones
            f.seek(0)
            f.write(b'\xFF' * file_size)
            f.flush()
            os.fsync(f.fileno())
            
            # Third pass: Overwrite with random data
            f.seek(0)
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())
        
        # Delete the file
        os.remove(file_path)
        print(f"Securely deleted file: {file_path}")
    except Exception as e:
        print(f"Error securely deleting file {file_path}: {str(e)}")
        # Fallback to regular delete
        try:
            os.remove(file_path)
            print(f"Performed regular delete of file: {file_path}")
        except:
            pass

def cleanup_temp_directories():
    """Clean up temporary directories created by RuneSlayer"""
    try:
        # Find all temporary directories with 'runeslayer_' prefix
        temp_dir = tempfile.gettempdir()
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path) and item.startswith('runeslayer_'):
                try:
                    # Clean up each directory
                    print(f"Cleaning up temp directory: {item_path}")
                    for root, dirs, files in os.walk(item_path, topdown=False):
                        for file in files:
                            file_path = os.path.join(root, file)
                            secure_delete_file(file_path)
                        for dir in dirs:
                            try:
                                dir_path = os.path.join(root, dir)
                                os.rmdir(dir_path)
                            except:
                                pass
                    # Remove the directory itself
                    os.rmdir(item_path)
                    print(f"Removed temp directory: {item_path}")
                except Exception as e:
                    print(f"Error cleaning up directory {item_path}: {str(e)}")
    except Exception as e:
        print(f"Error during temp directory cleanup: {str(e)}")

def empty_recycle_bin():
    """Empty the recycle bin/trash on the system"""
    try:
        # Determine the operating system
        if os.name == 'nt':  # Windows
            print("Emptying Windows Recycle Bin...")
            subprocess.run(['powershell.exe', 'Clear-RecycleBin', '-Force', '-ErrorAction', 'SilentlyContinue'], 
                           capture_output=True, check=False)
        elif sys.platform == 'darwin':  # macOS
            print("Emptying macOS Trash...")
            subprocess.run(['osascript', '-e', 'tell app "Finder" to empty trash'], 
                           capture_output=True, check=False)
        elif sys.platform.startswith('linux'):  # Linux
            # Different Linux distros handle trash differently, try common methods
            print("Emptying Linux Trash...")
            trash_dirs = [
                os.path.expanduser('~/.local/share/Trash'),
                os.path.expanduser('~/.Trash'),
            ]
            for trash_dir in trash_dirs:
                if os.path.exists(trash_dir):
                    try:
                        # Remove files in trash/files
                        files_dir = os.path.join(trash_dir, 'files')
                        if os.path.exists(files_dir):
                            for item in os.listdir(files_dir):
                                item_path = os.path.join(files_dir, item)
                                if os.path.isdir(item_path):
                                    shutil.rmtree(item_path, ignore_errors=True)
                                else:
                                    secure_delete_file(item_path)
                        
                        # Remove info files
                        info_dir = os.path.join(trash_dir, 'info')
                        if os.path.exists(info_dir):
                            for item in os.listdir(info_dir):
                                item_path = os.path.join(info_dir, item)
                                if not os.path.isdir(item_path):
                                    os.remove(item_path)
                    except Exception as e:
                        print(f"Error emptying trash directory {trash_dir}: {str(e)}")
    except Exception as e:
        print(f"Error emptying recycle bin: {str(e)}")

def perform_cleanup():
    """Perform all cleanup operations"""
    print("Starting secure cleanup...")
    
    # Get this script's path
    script_path = os.path.abspath(__file__)
    print(f"Script path: {script_path}")
    
    # Clean up temp directories
    cleanup_temp_directories()
    
    # Empty recycle bin
    empty_recycle_bin()
    
    # Lastly, try to securely delete this script (may not work as it's running)
    try:
        # Set the script to delete on exit
        # We can't reliably delete the running script, so we create a small batch file to do it
        if os.name == 'nt':  # Windows
            batch_path = os.path.join(tempfile.gettempdir(), f"cleanup_{uuid.uuid4().hex}.bat")
            with open(batch_path, "w") as f:
                f.write(f'@echo off\r\n')
                f.write(f'timeout /t 1 /nobreak > nul\r\n')
                f.write(f'del /F /Q "{script_path}"\r\n')
                f.write(f'del /F /Q "{batch_path}"\r\n')
            subprocess.Popen(f'start /min "" cmd /c "{batch_path}"', shell=True)
        else:  # Unix-like systems
            shell_path = os.path.join(tempfile.gettempdir(), f"cleanup_{uuid.uuid4().hex}.sh")
            with open(shell_path, "w") as f:
                f.write("#!/bin/sh\n")
                f.write(f"sleep 1\n")
                f.write(f"rm -f '{script_path}'\n")
                f.write(f"rm -f '{shell_path}'\n")
            os.chmod(shell_path, 0o755)
            subprocess.Popen(f"nohup {shell_path} >/dev/null 2>&1 &", shell=True)
    except Exception as e:
        print(f"Error setting up self-deletion: {str(e)}")
    
    print("Secure cleanup complete")

# Register the cleanup function to run on exit only if we're running in a temporary process
# Check for the environment variable set by the loader
if os.environ.get("RUNESLAYER_CLEANUP_ON_EXIT") == "1":
    print("Cleanup on exit enabled - will remove all traces when closing")
    atexit.register(perform_cleanup)
else:
    print("Running in development mode - cleanup disabled")

def main(user_info=None):
    """Main entry point"""
    try:
        # Check for cooldown
        on_cooldown, remaining_minutes = is_on_cooldown()
        if on_cooldown:
            # Convert remaining minutes to minutes and seconds
            remaining_mins = int(remaining_minutes)
            remaining_secs = int((remaining_minutes - remaining_mins) * 60)
            
            # Create a simple window to show cooldown message
            root = tk.Tk()
            root.title("RuneSlayer - Cooldown Active")
            root.geometry("450x200")
            root.configure(bg=COLORS["background"])
            root.resizable(False, False)
            
            # Center window
            root.update_idletasks()
            width = root.winfo_width()
            height = root.winfo_height()
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry(f'{width}x{height}+{x}+{y}')
            
            # Message frame
            msg_frame = tk.Frame(root, bg=COLORS["background"])
            msg_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            # Icon/Warning
            warning_label = tk.Label(
                msg_frame,
                text="⚠️",
                font=("Arial", 28),
                bg=COLORS["background"],
                fg=COLORS["warning"]
            )
            warning_label.pack(pady=(0, 10))
            
            # Title
            title_label = tk.Label(
                msg_frame,
                text="Cooldown Period Active",
                font=("Arial", 16, "bold"),
                bg=COLORS["background"],
                fg=COLORS["text_bright"]
            )
            title_label.pack(pady=(0, 10))
            
            # Message
            message = f"Please wait {remaining_mins} minutes and {remaining_secs} seconds before using RuneSlayer again."
            message_label = tk.Label(
                msg_frame,
                text=message,
                bg=COLORS["background"],
                fg=COLORS["text"],
                wraplength=350,
                justify=tk.CENTER
            )
            message_label.pack(pady=(0, 15))
            
            # Close button
            close_button = tk.Button(
                msg_frame,
                text="Close",
                bg=COLORS["primary"],
                fg=COLORS["text_bright"],
                activebackground=COLORS["primary_hover"],
                activeforeground=COLORS["text_bright"],
                relief=tk.FLAT,
                padx=20,
                pady=5,
                command=root.destroy
            )
            close_button.pack()
            
            # Start mainloop
            root.mainloop()
            return
        
        # Not on cooldown, create root window
        root = tk.Tk()
        
        # Create custom style for ttk widgets
        style = ttk.Style()
        style.theme_use('default')
        
        if user_info:
            # Skip auth and go straight to main app if user_info provided
            app = RuneSlayerTool(root, user_info)
            # Update cooldown file upon successful authentication
            update_cooldown_file()
        else:
            # Start with auth window if no user_info
            app = AuthenticationApp(root)
            # Authentication process will call update_cooldown_file after success
        
        # Add handler for window close event to ensure cleanup occurs (if needed)
        if os.environ.get("RUNESLAYER_CLEANUP_ON_EXIT") == "1":
            root.protocol("WM_DELETE_WINDOW", lambda: (perform_cleanup(), root.destroy()))
        else:
            root.protocol("WM_DELETE_WINDOW", root.destroy)
        
        # Start main loop
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_tb(e.__traceback__)

if __name__ == "__main__":
    main()
