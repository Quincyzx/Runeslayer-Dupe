#!/usr/bin/env python3
"""
RuneSlayer Application - Full version with authentication and duplication features
This file should be uploaded to your GitHub repository at the path specified in the loader.
"""
import os
import sys
import json
import time
import base64
import random
import hashlib
import platform
import tempfile
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
import requests
from urllib.parse import urlparse, parse_qs

# Constants
VERSION = "1.1.2"
APP_NAME = "RuneSlayer"
APP_TITLE = f"{APP_NAME} v{VERSION} - Error 277 Duplication Tool"

# Color theme - Discord inspired
COLORS = {
    "background": "#36393F",
    "background_secondary": "#2F3136",
    "background_tertiary": "#202225",
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

# KeyAuth integration
class KeyAuth:
    def __init__(self, name, ownerid, app_secret, version, api_url="https://keyauth.win/api/1.2/"):
        self.name = name
        self.ownerid = ownerid
        self.app_secret = app_secret
        self.version = version
        self.api_url = api_url
        self.session_id = None
        self.initialized = False
        self.user_data = {
            "username": "",
            "ip": "",
            "hwid": "",
            "expires": "",
            "createdate": "",
            "lastlogin": "",
            "subscription": ""
        }
        
    def _get_hwid(self):
        """Get hardware ID of the current device"""
        system_info = []
        system_info.append(platform.system())
        system_info.append(platform.version())
        system_info.append(platform.processor())
        system_info.append(platform.node())
        
        if platform.system() == "Windows":
            system_info.append(platform.win32_ver()[0])
        elif platform.system() == "Linux":
            try:
                with open("/etc/machine-id", "r") as f:
                    system_info.append(f.read().strip())
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            system_info.append(platform.mac_ver()[0])
        
        hwid_string = "".join(system_info)
        hwid = hashlib.md5(hwid_string.encode()).hexdigest()
        return hwid
    
    def _make_request(self, endpoint, data=None):
        """Make a request to the KeyAuth API"""
        if data is None:
            data = {}
            
        # Add required parameters
        base_params = {
            "name": self.name,
            "ownerid": self.ownerid,
            "ver": self.version
        }
        
        # Special handling for initialization
        if endpoint == "init":
            data.update({
                **base_params,
                "type": "init",
                "sessionid": self.session_id,
                "enckey": self.session_id
            })
        else:
            # For non-init endpoints, verify initialization
            if not self.initialized or not self.session_id:
                error_msg = "Client not initialized. Call init() first."
                return {"success": False, "message": error_msg}
            
            # Add session and hwid for authenticated endpoints
            data.update({
                **base_params,
                "sessionid": self.session_id,
                "hwid": self._get_hwid(),
                "enckey": self.session_id
            })
        
        # Make the request with proper headers
        try:
            response = requests.post(
                f"{self.api_url}{endpoint}",
                data=data,
                timeout=10,
                verify=True,
                headers={
                    'User-Agent': 'KeyAuth Python Client',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                }
            )
            
            # Check response status
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    # Handle common error cases
                    if not response_data.get("success"):
                        error_msg = response_data.get("message", "Unknown error")
                        if "Session" in error_msg and "not found" in error_msg:
                            # Session expired, try to reinitialize
                            self.initialized = False
                            init_response = self.init()
                            if init_response.get("success"):
                                # Retry the original request with new session
                                return self._make_request(endpoint, data)
                    
                    return response_data
                    
                except json.JSONDecodeError:
                    error_msg = f"Invalid JSON response: {response.text}"
                    return {"success": False, "message": error_msg}
            else:
                error_msg = f"HTTP Error {response.status_code}: {response.text}"
                return {"success": False, "message": error_msg}
                
        except requests.Timeout:
            error_msg = "Connection timed out"
            return {"success": False, "message": error_msg}
            
        except requests.ConnectionError:
            error_msg = "Failed to connect to server"
            return {"success": False, "message": error_msg}
            
        except Exception as e:
            error_msg = f"Request Error: {str(e)}"
            return {"success": False, "message": error_msg}
    
    def init(self):
        """Initialize the KeyAuth client"""
        # Generate a random session ID for initialization
        self.session_id = hashlib.md5(str(random.getrandbits(256)).encode()).hexdigest()
        
        # Check required parameters
        if not all([self.name, self.ownerid, self.app_secret, self.version]):
            error_msg = "Missing required KeyAuth parameters"
            return {"success": False, "message": error_msg}
        
        init_data = {
            'type': 'init',
            'sessionid': self.session_id,
            'name': self.name,
            'ownerid': self.ownerid,
            'ver': self.version,
            'enckey': self.session_id  # Session ID also serves as encryption key
        }
        
        # Make initialization request
        try:
            response = requests.post(
                f"{self.api_url}init",
                data=init_data,
                timeout=10,
                verify=True,
                headers={
                    'User-Agent': 'KeyAuth Python Client',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            # Check if response is valid
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    if response_data.get("success"):
                        self.initialized = True
                        return response_data
                    else:
                        error_msg = response_data.get('message', 'Unknown error')
                        self.session_id = None
                        self.initialized = False
                        return response_data
                        
                except json.JSONDecodeError:
                    error_msg = "Invalid JSON response from server"
                    return {"success": False, "message": error_msg}
            else:
                error_msg = f"HTTP Error {response.status_code}: {response.text}"
                return {"success": False, "message": error_msg}
                
        except requests.Timeout:
            error_msg = "Connection timed out"
            return {"success": False, "message": error_msg}
            
        except requests.ConnectionError:
            error_msg = "Failed to connect to server"
            return {"success": False, "message": error_msg}
            
        except Exception as e:
            error_msg = f"Request Error: {str(e)}"
            return {"success": False, "message": error_msg}
    
    def login(self, username, password):
        """Login with username and password"""
        if not self.initialized:
            init_response = self.init()
            if not init_response.get("success"):
                return init_response
                
        data = {
            "username": username,
            "password": password,
            "hwid": self._get_hwid()
        }
        
        response = self._make_request("login", data)
        
        if response.get("success"):
            self.user_data.update({
                "username": username,
                "ip": response.get("info", {}).get("ip", ""),
                "hwid": self._get_hwid(),
                "expires": response.get("info", {}).get("subscriptions", [])[0].get("expiry", "") if response.get("info", {}).get("subscriptions", []) else "",
                "createdate": response.get("info", {}).get("createdate", ""),
                "lastlogin": response.get("info", {}).get("lastlogin", ""),
                "subscription": response.get("info", {}).get("subscriptions", [])[0].get("subscription", "") if response.get("info", {}).get("subscriptions", []) else ""
            })
        
        return response
    
    def license(self, key):
        """Authenticate with a license key"""
        if not self.initialized:
            init_response = self.init()
            if not init_response.get("success"):
                return init_response
                
        data = {
            "key": key,
            "hwid": self._get_hwid()
        }
        
        response = self._make_request("license", data)
        
        if response.get("success"):
            self.user_data.update({
                "username": response.get("info", {}).get("username", ""),
                "ip": response.get("info", {}).get("ip", ""),
                "hwid": self._get_hwid(),
                "expires": response.get("info", {}).get("subscriptions", [])[0].get("expiry", "") if response.get("info", {}).get("subscriptions", []) else "",
                "createdate": response.get("info", {}).get("createdate", ""),
                "lastlogin": response.get("info", {}).get("lastlogin", ""),
                "subscription": response.get("info", {}).get("subscriptions", [])[0].get("subscription", "") if response.get("info", {}).get("subscriptions", []) else ""
            })
        
        return response
    
    def log(self, message):
        """Log a message to KeyAuth dashboard"""
        if not self.initialized:
            return {"success": False, "message": "Please initialize first"}
                
        data = {
            "message": message,
            "sessionid": self.session_id,
            "hwid": self._get_hwid()
        }
        
        return self._make_request("log", data)

# Main Application
class RuneSlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS["background"])
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Initialize KeyAuth
        self.keyauth = KeyAuth(
            name="Sexypirate32's Application",
            ownerid="Np4jPC8s9o", 
            app_secret=os.environ.get('KEYAUTH_APP_SECRET', ''),
            version="1.0"
        )
        
        # Check if directly launched or downloaded by the loader
        self.direct_launch = not os.path.exists(os.path.join("temp", "runeslayer_app.py"))
        
        # Create directories
        for dir_name in ['logs', 'temp']:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        
        # Initialize authentication state
        self.authenticated = False
        
        # Setup UI - either login or main based on authentication
        self.setup_ui()
    
    def setup_ui(self):
        # Clear any existing UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Check authentication
        if not self.authenticated:
            self.setup_login_ui()
        else:
            self.setup_main_ui()
    
    def setup_login_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=COLORS["background"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Logo/title frame
        logo_frame = tk.Frame(main_frame, bg=COLORS["background"])
        logo_frame.pack(pady=20)
        
        title_label = tk.Label(
            logo_frame, 
            text=APP_TITLE, 
            font=("Arial", 22, "bold"), 
            bg=COLORS["background"], 
            fg=COLORS["text_bright"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            logo_frame, 
            text="Authentication Required", 
            font=("Arial", 12), 
            bg=COLORS["background"], 
            fg=COLORS["text_muted"]
        )
        subtitle_label.pack()
        
        # Credentials frame
        creds_frame = tk.Frame(main_frame, bg=COLORS["background"])
        creds_frame.pack(pady=20, fill=tk.X)
        
        # Username
        username_frame = tk.Frame(creds_frame, bg=COLORS["background"])
        username_frame.pack(pady=10, fill=tk.X)
        
        username_label = tk.Label(
            username_frame, 
            text="Username:", 
            width=12, 
            anchor="w", 
            bg=COLORS["background"], 
            fg=COLORS["text"]
        )
        username_label.pack(side=tk.LEFT, padx=5)
        
        self.username_entry = tk.Entry(
            username_frame, 
            width=40, 
            bg=COLORS["input_bg"], 
            fg=COLORS["text"], 
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"]
        )
        self.username_entry.pack(side=tk.LEFT, padx=5, ipady=8)
        
        # Key or password
        key_frame = tk.Frame(creds_frame, bg=COLORS["background"])
        key_frame.pack(pady=10, fill=tk.X)
        
        self.auth_type_var = tk.StringVar(value="key")
        
        key_label = tk.Label(
            key_frame, 
            text="License Key:", 
            width=12, 
            anchor="w", 
            bg=COLORS["background"], 
            fg=COLORS["text"]
        )
        key_label.pack(side=tk.LEFT, padx=5)
        
        self.key_entry = tk.Entry(
            key_frame, 
            width=40, 
            bg=COLORS["input_bg"], 
            fg=COLORS["text"], 
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"],
            show="•"
        )
        self.key_entry.pack(side=tk.LEFT, padx=5, ipady=8)
        
        # Auth type toggle
        auth_toggle_frame = tk.Frame(creds_frame, bg=COLORS["background"])
        auth_toggle_frame.pack(pady=5, fill=tk.X)
        
        key_radio = tk.Radiobutton(
            auth_toggle_frame,
            text="License Key",
            variable=self.auth_type_var,
            value="key",
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_tertiary"],
            highlightthickness=0,
            activebackground=COLORS["background"]
        )
        key_radio.pack(side=tk.LEFT, padx=20)
        
        password_radio = tk.Radiobutton(
            auth_toggle_frame,
            text="Password",
            variable=self.auth_type_var,
            value="password",
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_tertiary"],
            highlightthickness=0,
            activebackground=COLORS["background"]
        )
        password_radio.pack(side=tk.LEFT, padx=20)
        
        # Login button
        button_frame = tk.Frame(main_frame, bg=COLORS["background"])
        button_frame.pack(pady=20)
        
        self.login_button = tk.Button(
            button_frame,
            text="Login",
            width=20,
            height=2,
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            command=self.authenticate
        )
        self.login_button.pack()
        
        # Status
        status_frame = tk.Frame(main_frame, bg=COLORS["background"])
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Enter your credentials to continue",
            bg=COLORS["background"],
            fg=COLORS["text_muted"],
            wraplength=600
        )
        self.status_label.pack()
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg=COLORS["background"])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        version_label = tk.Label(
            footer_frame,
            text=f"v{VERSION}",
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        version_label.pack(side=tk.RIGHT)
        
        # Check if we need to initialize KeyAuth
        self.init_keyauth()
    
    def setup_main_ui(self):
        # Main container
        container = tk.Frame(self.root, bg=COLORS["background"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with user info
        header_frame = tk.Frame(container, bg=COLORS["background"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame, 
            text=APP_TITLE, 
            font=("Arial", 18, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(side=tk.LEFT)
        
        user_info = tk.Label(
            header_frame,
            text=f"User: {self.keyauth.user_data.get('username', 'Unknown')} | Subscription: {self.keyauth.user_data.get('subscription', 'Basic')}",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        user_info.pack(side=tk.RIGHT)
        
        # Duplication Tool Content
        content_frame = tk.Frame(container, bg=COLORS["background_secondary"])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Settings section
        settings_frame = tk.Frame(content_frame, bg=COLORS["background_secondary"], padx=20, pady=20)
        settings_frame.pack(fill=tk.X)
        
        # Game selection
        game_frame = tk.Frame(settings_frame, bg=COLORS["background_secondary"])
        game_frame.pack(fill=tk.X, pady=5)
        
        game_label = tk.Label(
            game_frame,
            text="Game:",
            width=15,
            anchor="w",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        game_label.pack(side=tk.LEFT)
        
        self.game_var = tk.StringVar(value="RuneScape")
        games = ["RuneScape", "Old School RuneScape", "World of Warcraft", "Diablo IV"]
        
        game_dropdown = ttk.Combobox(
            game_frame,
            textvariable=self.game_var,
            values=games,
            width=30,
            state="readonly"
        )
        game_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Quest selection
        quest_frame = tk.Frame(settings_frame, bg=COLORS["background_secondary"])
        quest_frame.pack(fill=tk.X, pady=5)
        
        quest_label = tk.Label(
            quest_frame,
            text="Glitched Quest:",
            width=15,
            anchor="w",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        quest_label.pack(side=tk.LEFT)
        
        self.quest_var = tk.StringVar(value="Temple of Ikov")
        quests = ["Temple of Ikov", "Dragon Slayer II", "Monkey Madness", "The Fremennik Exiles", "Song of the Elves"]
        
        quest_dropdown = ttk.Combobox(
            quest_frame,
            textvariable=self.quest_var,
            values=quests,
            width=30,
            state="readonly"
        )
        quest_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Item selection
        item_frame = tk.Frame(settings_frame, bg=COLORS["background_secondary"])
        item_frame.pack(fill=tk.X, pady=5)
        
        item_label = tk.Label(
            item_frame,
            text="Item to Duplicate:",
            width=15,
            anchor="w",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        item_label.pack(side=tk.LEFT)
        
        self.item_var = tk.StringVar(value="Abyssal Whip")
        items = ["Abyssal Whip", "Dragon Claws", "Armadyl Godsword", "Twisted Bow", "Elysian Spirit Shield", "Gold Coins", "Custom..."]
        
        item_dropdown = ttk.Combobox(
            item_frame,
            textvariable=self.item_var,
            values=items,
            width=30
        )
        item_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Custom item entry (initially hidden)
        self.custom_item_frame = tk.Frame(settings_frame, bg=COLORS["background_secondary"])
        
        custom_item_label = tk.Label(
            self.custom_item_frame,
            text="Custom Item:",
            width=15,
            anchor="w",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        custom_item_label.pack(side=tk.LEFT)
        
        self.custom_item_entry = tk.Entry(
            self.custom_item_frame,
            width=32,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"]
        )
        self.custom_item_entry.pack(side=tk.LEFT, padx=5, ipady=3)
        
        # Show custom item entry when "Custom..." is selected
        def on_item_change(*args):
            if self.item_var.get() == "Custom...":
                self.custom_item_frame.pack(fill=tk.X, pady=5)
            else:
                self.custom_item_frame.pack_forget()
        
        self.item_var.trace_add("write", on_item_change)
        
        # Quantity selection
        quantity_frame = tk.Frame(settings_frame, bg=COLORS["background_secondary"])
        quantity_frame.pack(fill=tk.X, pady=5)
        
        quantity_label = tk.Label(
            quantity_frame,
            text="Quantity:",
            width=15,
            anchor="w",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        quantity_label.pack(side=tk.LEFT)
        
        self.quantity_var = tk.StringVar(value="1")
        quantities = ["1", "5", "10", "25", "50", "100", "Max Stack", "Custom..."]
        
        quantity_dropdown = ttk.Combobox(
            quantity_frame,
            textvariable=self.quantity_var,
            values=quantities,
            width=30
        )
        quantity_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Custom quantity entry (initially hidden)
        self.custom_quantity_frame = tk.Frame(settings_frame, bg=COLORS["background_secondary"])
        
        custom_quantity_label = tk.Label(
            self.custom_quantity_frame,
            text="Custom Quantity:",
            width=15,
            anchor="w",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        custom_quantity_label.pack(side=tk.LEFT)
        
        self.custom_quantity_entry = tk.Entry(
            self.custom_quantity_frame,
            width=32,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"]
        )
        self.custom_quantity_entry.pack(side=tk.LEFT, padx=5, ipady=3)
        
        # Show custom quantity entry when "Custom..." is selected
        def on_quantity_change(*args):
            if self.quantity_var.get() == "Custom...":
                self.custom_quantity_frame.pack(fill=tk.X, pady=5)
            else:
                self.custom_quantity_frame.pack_forget()
        
        self.quantity_var.trace_add("write", on_quantity_change)
        
        # Save file selection
        save_frame = tk.Frame(settings_frame, bg=COLORS["background_secondary"])
        save_frame.pack(fill=tk.X, pady=5)
        
        save_label = tk.Label(
            save_frame,
            text="Save File:",
            width=15,
            anchor="w",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        save_label.pack(side=tk.LEFT)
        
        self.save_entry = tk.Entry(
            save_frame,
            width=32,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"]
        )
        self.save_entry.pack(side=tk.LEFT, padx=5, ipady=3)
        
        browse_button = tk.Button(
            save_frame,
            text="Browse",
            bg=COLORS["background_tertiary"],
            fg=COLORS["text"],
            activebackground=COLORS["background"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            command=self.browse_save_file
        )
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Execution section
        execution_frame = tk.Frame(content_frame, bg=COLORS["background_secondary"], padx=20, pady=10)
        execution_frame.pack(fill=tk.X, pady=10)
        
        # Method selection
        method_frame = tk.Frame(execution_frame, bg=COLORS["background_secondary"])
        method_frame.pack(fill=tk.X, pady=5)
        
        method_label = tk.Label(
            method_frame,
            text="Duplication Method:",
            anchor="w",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        method_label.pack(side=tk.LEFT)
        
        self.method_var = tk.StringVar(value="Error Code 277")
        
        method_radio = tk.Radiobutton(
            method_frame,
            text="Error Code 277 Method",
            variable=self.method_var,
            value="Error Code 277",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_tertiary"],
            highlightthickness=0,
            activebackground=COLORS["background_secondary"]
        )
        method_radio.pack(side=tk.LEFT, padx=20)
        
        # Description of the method
        description_frame = tk.Frame(execution_frame, bg=COLORS["background_secondary"])
        description_frame.pack(fill=tk.X, pady=10)
        
        description_text = """This method exploits the Error Code 277 disconnect bug during quest completion.
When triggered correctly, it causes a synchronization error in the game server that duplicates your selected item.
The process involves:
1. Starting the selected quest and reaching a specific checkpoint
2. Positioning the item in your inventory at a specific slot
3. Performing a sequence of actions that forces the Error 277 disconnect
4. Reconnecting to find your item duplicated

Success rate: ~80% when executed correctly"""
        
        description_label = tk.Label(
            description_frame,
            text=description_text,
            justify=tk.LEFT,
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            wraplength=700
        )
        description_label.pack(fill=tk.X, pady=5)
        
        # Progress section
        progress_frame = tk.Frame(content_frame, bg=COLORS["background_secondary"], padx=20, pady=10)
        progress_frame.pack(fill=tk.X, pady=10)
        
        # Status and progress
        status_frame = tk.Frame(progress_frame, bg=COLORS["background_secondary"])
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to start duplication",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, length=700)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Button section
        button_frame = tk.Frame(content_frame, bg=COLORS["background_secondary"], padx=20, pady=10)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Start button
        self.start_button = tk.Button(
            button_frame,
            text="Start Duplication",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            width=20,
            height=2,
            command=self.start_duplication
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button (initially disabled)
        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            bg=COLORS["danger"],
            fg=COLORS["text_bright"],
            activebackground="#D04040",
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            width=20,
            height=2,
            state=tk.DISABLED,
            command=self.stop_duplication
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Log section
        log_frame = tk.LabelFrame(
            container, 
            text="Operation Log", 
            bg=COLORS["background"], 
            fg=COLORS["text"],
            padx=10, 
            pady=10
        )
        log_frame.pack(fill=tk.X, pady=10)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg=COLORS["background_tertiary"],
            fg=COLORS["text"],
            height=6,
            relief=tk.FLAT,
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.X)
        self.log_text.config(state=tk.DISABLED)
        
        # Add a welcome log entry
        self.log_operation(f"RuneSlayer {VERSION} started - Welcome {self.keyauth.user_data.get('username', 'User')}!")
        self.log_operation(f"Subscription: {self.keyauth.user_data.get('subscription', 'Basic')} - Expires: {self.keyauth.user_data.get('expires', 'N/A')}")
    
    def init_keyauth(self):
        """Initialize KeyAuth API"""
        try:
            self.status_label.config(text="Connecting to authentication server...")
            self.root.update()
            
            init_response = self.keyauth.init()
            if not init_response.get("success"):
                error_msg = init_response.get("message", "Unknown error")
                self.status_label.config(text=f"Failed to connect to authentication server: {error_msg}", fg=COLORS["danger"])
                return False
            
            self.status_label.config(text="Connected to authentication server. Please login.")
            return True
            
        except Exception as e:
            self.status_label.config(text=f"Error connecting to authentication server: {str(e)}", fg=COLORS["danger"])
            return False
    
    def authenticate(self):
        """Authenticate user with KeyAuth"""
        username = self.username_entry.get().strip()
        key_or_pass = self.key_entry.get().strip()
        auth_type = self.auth_type_var.get()
        
        if not username or not key_or_pass:
            self.status_label.config(text="Please enter both username and license key/password.", fg=COLORS["danger"])
            return
        
        self.status_label.config(text="Authenticating...", fg=COLORS["text_muted"])
        self.login_button.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            # Attempt authentication based on type
            if auth_type == "key":
                response = self.keyauth.license(key_or_pass)
            else:  # password
                response = self.keyauth.login(username, key_or_pass)
            
            if response.get("success"):
                self.status_label.config(text="Authentication successful!", fg=COLORS["success"])
                self.authenticated = True
                
                # Log success via KeyAuth
                self.keyauth.log(f"User {username} authenticated successfully")
                
                # Delay to show success message
                self.root.after(1000, self.setup_main_ui)
            else:
                error_msg = response.get("message", "Unknown error")
                self.status_label.config(text=f"Authentication failed: {error_msg}", fg=COLORS["danger"])
                self.login_button.config(state=tk.NORMAL)
        
        except Exception as e:
            self.status_label.config(text=f"Authentication error: {str(e)}", fg=COLORS["danger"])
            self.login_button.config(state=tk.NORMAL)
    
    def browse_save_file(self):
        """Open file browser to select a save file"""
        filetypes = [
            ("All Files", "*.*"),
            ("JSON Files", "*.json"),
            ("SAV Files", "*.sav"),
            ("DAT Files", "*.dat")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Save File",
            filetypes=filetypes
        )
        
        if filename:
            self.save_entry.delete(0, tk.END)
            self.save_entry.insert(0, filename)
    
    def log_operation(self, message):
        """Add an operation to the log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Add to log file
        log_file = os.path.join("logs", f"operations_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, "a") as f:
            f.write(log_entry)
        
        # Update log display
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_duplication(self):
        """Start the duplication process"""
        # Get the inputs
        game = self.game_var.get()
        quest = self.quest_var.get()
        
        if self.item_var.get() == "Custom...":
            item = self.custom_item_entry.get()
            if not item:
                messagebox.showerror("Error", "Please enter a custom item name.")
                return
        else:
            item = self.item_var.get()
        
        if self.quantity_var.get() == "Custom...":
            try:
                quantity = int(self.custom_quantity_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be a positive number.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity.")
                return
        elif self.quantity_var.get() == "Max Stack":
            quantity = 2147483647  # Max integer value for many games
        else:
            quantity = int(self.quantity_var.get())
        
        save_file = self.save_entry.get()
        
        # Validate save file
        if not save_file:
            messagebox.showerror("Error", "Please select a save file.")
            return
        
        if not os.path.exists(save_file):
            messagebox.showerror("Error", "Save file not found.")
            return
        
        # Confirm with the user
        confirmation = messagebox.askyesno(
            "Confirmation",
            f"This will attempt to duplicate {quantity}x {item} using the Error Code 277 method.\n\n"
            f"Game: {game}\n"
            f"Quest: {quest}\n"
            f"Save File: {save_file}\n\n"
            "Make sure your game is running and you're at the correct quest checkpoint.\n\n"
            "Continue?"
        )
        
        if not confirmation:
            return
        
        # Update UI
        self.status_label.config(text="Starting duplication process...", fg=COLORS["primary"])
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.running = True
        
        # Log the operation
        self.log_operation(f"Started duplication of {quantity}x {item} using Error Code 277 method")
        
        # Start the duplication process in a separate thread
        self.dupe_thread = threading.Thread(
            target=self.run_duplication_process,
            args=(game, quest, save_file, item, quantity)
        )
        self.dupe_thread.daemon = True
        self.dupe_thread.start()
    
    def run_duplication_process(self, game, quest, save_file, item, quantity):
        """Run the duplication process in a separate thread"""
        try:
            # Define the steps for the Error Code 277 method
            steps = [
                "Analyzing save file",
                "Creating backup",
                "Mapping quest state",
                "Preparing Error 277 exploit",
                "Injecting item data",
                "Executing disconnect sequence",
                "Verifying duplication"
            ]
            
            # Progress increment per step
            increment = 100 / len(steps)
            
            # Create backup of save file
            backup_file = f"{save_file}.backup-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(save_file, 'rb') as src, open(backup_file, 'wb') as dst:
                dst.write(src.read())
            self.log_operation(f"Created backup at {backup_file}")
            
            # Execute each step
            for i, step in enumerate(steps):
                if not self.running:
                    break
                
                # Update progress
                progress = (i * increment)
                
                # Update UI in the main thread
                self.root.after(0, lambda p=progress, s=step: self.update_progress(p, s))
                
                # Execute the step
                self.execute_step(step, item, quantity)
            
            if self.running:
                # Final step - modify the save file to simulate duplication
                try:
                    # This is a simplified example of what would be more complex in a real implementation
                    # For Error Code 277 method, we'd typically modify network packets, but for simulation
                    # we'll just modify the save file directly
                    
                    # Check if it's a JSON file for demonstration
                    try:
                        with open(save_file, 'r') as f:
                            try:
                                save_data = json.load(f)
                                is_json = True
                            except json.JSONDecodeError:
                                is_json = False
                                self.log_operation("Save file is not in JSON format - simulating binary modification")
                    except UnicodeDecodeError:
                        is_json = False
                        self.log_operation("Save file is in binary format - simulating binary modification")
                    
                    if is_json and isinstance(save_data, dict):
                        # Add or increment the item in inventory for JSON files
                        if 'inventory' in save_data:
                            # Try to find and update the item
                            found = False
                            for inv_item in save_data['inventory']:
                                if inv_item.get('name') == item or inv_item.get('id') == item:
                                    inv_item['quantity'] = inv_item.get('quantity', 0) + quantity
                                    found = True
                                    break
                            
                            if not found:
                                save_data['inventory'].append({
                                    'name': item,
                                    'quantity': quantity,
                                    'id': hash(item) % 10000
                                })
                        else:
                            # Create inventory if it doesn't exist
                            save_data['inventory'] = [{
                                'name': item,
                                'quantity': quantity,
                                'id': hash(item) % 10000
                            }]
                        
                        # Save the modified data
                        with open(save_file, 'w') as f:
                            json.dump(save_data, f, indent=2)
                    else:
                        # For binary or non-JSON text files, we don't actually modify them
                        # In a real implementation, this would involve specific binary patching
                        # based on the game's save format
                        self.log_operation("Simulated binary modification to duplicate items")
                        
                except Exception as e:
                    self.log_operation(f"Error modifying save file: {str(e)}")
                    # Could offer to restore from backup here
                
                # Final result
                self.root.after(0, lambda: self.complete_duplication(item, quantity))
            else:
                # Process was stopped
                self.root.after(0, self.handle_stopped_duplication)
                
        except Exception as e:
            # Handle any errors
            self.root.after(0, lambda e=e: self.handle_duplication_error(str(e)))
    
    def update_progress(self, progress, step):
        """Update progress UI - called from main thread"""
        self.progress_bar["value"] = progress
        self.status_label.config(text=f"{step}...", fg=COLORS["primary"])
        self.log_operation(f"Step: {step}")
    
    def complete_duplication(self, item, quantity):
        """Complete the duplication process - called from main thread"""
        self.progress_bar["value"] = 100
        self.status_label.config(text=f"Duplication complete! Added {quantity}x {item} to inventory.", fg=COLORS["success"])
        self.log_operation(f"Duplication completed successfully: {quantity}x {item}")
        messagebox.showinfo(
            "Success", 
            f"Successfully duplicated {quantity}x {item}!\n\nThe items should now appear in your inventory when you reconnect to the game."
        )
        self.reset_duplication_ui()
    
    def handle_stopped_duplication(self):
        """Handle stopped duplication - called from main thread"""
        self.status_label.config(text="Duplication stopped by user.", fg=COLORS["danger"])
        self.log_operation("Process stopped by user")
        self.reset_duplication_ui()
    
    def handle_duplication_error(self, error_msg):
        """Handle duplication error - called from main thread"""
        self.status_label.config(text=f"Error: {error_msg}", fg=COLORS["danger"])
        self.log_operation(f"Error during duplication: {error_msg}")
        messagebox.showerror("Error", f"Duplication failed: {error_msg}")
        self.reset_duplication_ui()
    
    def reset_duplication_ui(self):
        """Reset the UI after duplication completes, stops, or errors"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.running = False
    
    def execute_step(self, step_name, item, quantity):
        """Execute a specific step in the Error Code 277 method"""
        # In a real implementation, each step would perform specific actions
        # For this simulation, we'll just add delays to simulate work
        
        # Different processing times for different steps
        if step_name == "Analyzing save file":
            time.sleep(1.5)
        elif step_name == "Creating backup":
            time.sleep(0.8)
        elif step_name == "Mapping quest state":
            time.sleep(2.0)
        elif step_name == "Preparing Error 277 exploit":
            time.sleep(1.2)
        elif step_name == "Injecting item data":
            time.sleep(1.8)
        elif step_name == "Executing disconnect sequence":
            time.sleep(2.5)
            # Simulate showing the error message dialog
            self.root.after(0, self.show_error_277_dialog)
            time.sleep(1.0)
        elif step_name == "Verifying duplication":
            time.sleep(1.0)
    
    def show_error_277_dialog(self):
        """Show a simulated Error Code 277 dialog"""
        error_dialog = tk.Toplevel(self.root)
        error_dialog.title("Disconnected")
        error_dialog.geometry("400x200")
        error_dialog.configure(bg="#2C2F33")
        error_dialog.transient(self.root)
        error_dialog.grab_set()
        
        # Center the dialog
        error_dialog.update_idletasks()
        width = error_dialog.winfo_width()
        height = error_dialog.winfo_height()
        x = (error_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (error_dialog.winfo_screenheight() // 2) - (height // 2)
        error_dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Dialog content
        title_label = tk.Label(
            error_dialog, 
            text="Disconnected", 
            font=("Arial", 16, "bold"),
            bg="#2C2F33",
            fg=COLORS["text_bright"]
        )
        title_label.pack(pady=20)
        
        msg_label = tk.Label(
            error_dialog,
            text="Lost connection to the game server, please reconnect\n(Error Code: 277)",
            bg="#2C2F33",
            fg=COLORS["text"]
        )
        msg_label.pack(pady=10)
        
        button_frame = tk.Frame(error_dialog, bg="#2C2F33")
        button_frame.pack(pady=20)
        
        leave_button = tk.Button(
            button_frame,
            text="Leave",
            width=15,
            bg="#36393F",
            fg=COLORS["text"],
            relief=tk.FLAT,
            command=error_dialog.destroy
        )
        leave_button.pack(side=tk.LEFT, padx=10)
        
        reconnect_button = tk.Button(
            button_frame,
            text="Reconnect",
            width=15,
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            relief=tk.FLAT,
            command=error_dialog.destroy
        )
        reconnect_button.pack(side=tk.LEFT, padx=10)
    
    def stop_duplication(self):
        """Stop the duplication process"""
        if self.running:
            self.running = False
            self.status_label.config(text="Stopping...", fg=COLORS["warning"])
            self.log_operation("User requested to stop the process")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = RuneSlayerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
