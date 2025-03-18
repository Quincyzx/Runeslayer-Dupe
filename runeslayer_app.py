#!/usr/bin/env python3
"""
RuneSlayer Application - Full version with authentication and duplication features
This file should be uploaded to your GitHub repository at the path specified in the loader.
"""
import os
import sys
import json
import time
import random
import tkinter as tk
import threading
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

# Try to import KeyAuth client
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
    from keyauth import KeyAuth
except ImportError:
    print("ERROR: KeyAuth client not found. Please ensure it's installed in the lib directory.")
    sys.exit(1)

# Try to import Discord theme
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'styles'))
    from discord_theme import DiscordTheme, apply_discord_style_to_ttk
except ImportError:
    print("ERROR: Discord theme not found. Please ensure it's installed in the styles directory.")
    sys.exit(1)

# Constants
APP_TITLE = "RuneSlayer v1.1.2 - Error 277 Duplication Tool"
VERSION = "1.1.2"

# KeyAuth credentials
KEYAUTH_NAME = "Sexypirate32's Application"
KEYAUTH_OWNERID = "Np4jPC8s9o"
KEYAUTH_SECRET = os.environ.get('KEYAUTH_APP_SECRET', 'JnNLWXHXjS')  # Will be hardcoded in final EXE
KEYAUTH_VERSION = "1.0"

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

# Game data
GAME_DATA = {
    "Elden Ring": {
        "items": [
            "Lordsworn's Greatsword", "Uchigatana", "Rivers of Blood", "Moonveil", 
            "Golden Order Greatsword", "Sword of Night and Flame", "Bloodhound's Fang",
            "Dragonscale Blade", "Twinned Knight Swords", "Starscourge Greatsword",
            "Rune Arc", "Larval Tear", "Smithing Stone", "Somber Smithing Stone",
            "Flask of Wondrous Physick", "Golden Rune (1)", "Golden Rune (12)",
            "Lord's Rune", "Ancient Dragon Smithing Stone", "Rotten Winged Sword Insignia"
        ],
        "quests": [
            "Varre's Quest", "Three Fingers Questline", "Ranni's Questline", 
            "Volcano Manor Quest", "Millicent's Quest", "Nepheli Loux's Quest"
        ]
    },
    "Dark Souls 3": {
        "items": [
            "Estus Shard", "Undead Bone Shard", "Titanite Shard", "Large Titanite Shard",
            "Titanite Chunk", "Titanite Slab", "Ember", "Soul of a Great Champion",
            "Coiled Sword Fragment", "Lothric Knight Sword", "Irithyll Straight Sword",
            "Fume Ultra Greatsword", "Farron Greatsword", "Ringed Knight Paired Greatswords",
            "Dragonslayer Greataxe", "Sunlight Straight Sword", "Black Knight Glaive",
            "Grass Crest Shield", "Havel's Ring+3", "Ring of Favor+3"
        ],
        "quests": [
            "Siegward's Quest", "Anri's Quest", "Greirat's Quest", 
            "Leonhard's Quest", "Sirris's Quest", "Orbeck's Quest"
        ]
    },
    "Demon's Souls": {
        "items": [
            "Pure Bladestone", "Colorless Demon's Soul", "Ceramic Coin", 
            "Northern Regalia", "Kris Blade", "Penetrating Sword", 
            "Istarelle", "Large Sword of Searching", "Blueblood Sword",
            "Dark Silver Shield", "Talisman of Beasts", "Stonefang Ore",
            "Moonlightstone", "Dragonstone", "Marrowstone", "Darkmoonstone",
            "Soul of the Mind", "Soul of the Lost", "Renowned Hero's Soul",
            "Venerable Sage's Soul"
        ],
        "quests": [
            "Mephistopheles Quest", "Ostrava's Quest", "Yuria's Quest",
            "Saint Urbain's Quest", "Patches' Quest", "Sage Freke's Quest"
        ]
    },
    "Bloodborne": {
        "items": [
            "Blood Stone Shard", "Twin Blood Stone Shards", "Blood Stone Chunk",
            "Blood Rock", "Blood Vial", "Quicksilver Bullets", "Saw Cleaver",
            "Ludwig's Holy Blade", "Chikage", "Burial Blade", "Holy Moonlight Sword",
            "Rakuyo", "Beast Claw", "Whirligig Saw", "Beast Blood Pellet",
            "Madman's Knowledge", "Great One's Wisdom", "Blood Echoes Pouch",
            "Red Jeweled Brooch", "Moon Rune"
        ],
        "quests": [
            "Eileen the Crow's Quest", "Alfred's Quest", "Valtr's Quest",
            "Adella's Quest", "Arianna's Quest", "Old Hunter Djura's Quest"
        ]
    }
}

class RuneSlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("850x650")
        self.root.minsize(850, 650)
        self.root.configure(bg=COLORS["background"])
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Apply Discord styling to ttk widgets
        apply_discord_style_to_ttk()
        
        # Variables
        self.authenticated = False
        self.duplication_running = False
        self.stop_duplication = False
        
        # Settings
        self.settings = {
            "auto_save": True,
            "auto_backup": True,
            "show_popups": True,
            "dark_mode": True,
            "animation_speed": 5
        }
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        if not self.authenticated:
            self.setup_login_ui()
        else:
            self.setup_main_ui()
    
    def setup_login_ui(self):
        """Set up the login UI"""
        # Main container
        self.login_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(
            self.login_frame,
            text="RuneSlayer v1.1.2",
            font=("Arial", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = tk.Label(
            self.login_frame,
            text="Error 277 Duplication Tool",
            font=("Arial", 14),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        subtitle_label.pack(pady=(0, 5))
        
        auth_label = tk.Label(
            self.login_frame,
            text="Authentication Required",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        auth_label.pack(pady=(0, 20))
        
        # Login container
        login_container = tk.Frame(self.login_frame, bg=COLORS["background"], padx=10, pady=10)
        login_container.pack()
        
        # Username
        username_label = tk.Label(
            login_container,
            text="Username:",
            anchor="w",
            width=10,
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        username_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(
            login_container,
            textvariable=self.username_var,
            width=30,
            bg=COLORS["input_bg"],
            fg=COLORS["text_bright"],
            insertbackground=COLORS["text_bright"],
            relief=tk.FLAT,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        username_entry.grid(row=0, column=1, pady=(0, 10))
        
        # License Key
        key_label = tk.Label(
            login_container,
            text="License Key:",
            anchor="w",
            width=10,
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        key_label.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        self.key_var = tk.StringVar()
        self.key_var.set("KEYAUTH-3HDRVy-cKq0sW-4zb90X-MCG3jP-9FkfE1-n7CKF4")  # Pre-filled for testing
        
        key_entry = tk.Entry(
            login_container,
            textvariable=self.key_var,
            width=30,
            bg=COLORS["input_bg"],
            fg=COLORS["text_bright"],
            insertbackground=COLORS["text_bright"],
            relief=tk.FLAT,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        key_entry.grid(row=1, column=1, pady=(0, 10))
        
        # Login options
        options_frame = tk.Frame(login_container, bg=COLORS["background"])
        options_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        self.auth_method = tk.StringVar(value="license")
        
        license_radio = tk.Radiobutton(
            options_frame,
            text="License Key",
            variable=self.auth_method,
            value="license",
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"]
        )
        license_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        password_radio = tk.Radiobutton(
            options_frame,
            text="Password",
            variable=self.auth_method,
            value="password",
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"]
        )
        password_radio.pack(side=tk.LEFT)
        
        # Login button
        login_button_frame = tk.Frame(login_container, bg=COLORS["background"])
        login_button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        self.login_button = tk.Button(
            login_button_frame,
            text="Login",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            width=15,
            padx=10,
            pady=8,
            command=self.authenticate
        )
        self.login_button.pack()
        
        # Status message
        self.login_status_var = tk.StringVar()
        self.login_status_label = tk.Label(
            login_container,
            textvariable=self.login_status_var,
            bg=COLORS["background"],
            fg=COLORS["danger"],
            wraplength=350
        )
        self.login_status_label.grid(row=4, column=0, columnspan=2, pady=(15, 0))
        
        # Version
        version_label = tk.Label(
            self.login_frame,
            text=f"v{VERSION}",
            bg=COLORS["background"],
            fg=COLORS["text_muted"],
            anchor="e"
        )
        version_label.pack(pady=(20, 0), anchor="se")
        
        # Initialize KeyAuth
        self.init_keyauth()
    
    def init_keyauth(self):
        """Initialize KeyAuth API"""
        self.login_status_var.set("Connecting to authentication server...")
        self.login_button.config(state=tk.DISABLED)
        self.root.update()
        
        # Create KeyAuth instance
        self.keyauth = KeyAuth(
            name=KEYAUTH_NAME,
            ownerid=KEYAUTH_OWNERID, 
            app_secret=KEYAUTH_SECRET,
            version=KEYAUTH_VERSION
        )
        
        # Initialize
        status, message = self.keyauth.init()
        
        if not status:
            self.login_status_var.set(f"Failed to connect to authentication server: {message}")
            self.login_button.config(state=tk.NORMAL)
        else:
            self.login_status_var.set("Connected to authentication server")
            self.login_status_label.config(fg=COLORS["success"])
            self.login_button.config(state=tk.NORMAL)
    
    def authenticate(self):
        """Authenticate user with KeyAuth"""
        username = self.username_var.get().strip()
        key_or_password = self.key_var.get().strip()
        auth_method = self.auth_method.get()
        
        if not key_or_password:
            self.login_status_var.set("Please enter a license key or password")
            self.login_status_label.config(fg=COLORS["danger"])
            return
        
        if auth_method == "password" and not username:
            self.login_status_var.set("Please enter a username")
            self.login_status_label.config(fg=COLORS["danger"])
            return
        
        # Show loading message
        self.login_status_var.set("Authenticating...")
        self.login_status_label.config(fg=COLORS["text"])
        self.login_button.config(state=tk.DISABLED)
        self.root.update()
        
        # Try to authenticate
        if auth_method == "license":
            status, message = self.keyauth.license(key_or_password)
        else:  # auth_method == "password"
            status, message = self.keyauth.login(username, key_or_password)
        
        if status:
            # Log success via KeyAuth
            self.keyauth.log(f"User authenticated successfully")
            
            # Destroy login frame and load main UI
            self.authenticated = True
            self.login_frame.destroy()
            self.setup_main_ui()
        else:
            self.login_status_var.set(f"Authentication failed: {message}")
            self.login_status_label.config(fg=COLORS["danger"])
            self.login_button.config(state=tk.NORMAL)
    
    def setup_main_ui(self):
        """Setup the main UI after authentication"""
        # Create main container
        self.main_container = tk.Frame(self.root, bg=COLORS["background"])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        header = tk.Frame(self.main_container, bg=COLORS["background_secondary"], height=50)
        header.pack(fill=tk.X)
        
        title_label = tk.Label(
            header,
            text=APP_TITLE,
            font=("Arial", 14, "bold"),
            bg=COLORS["background_secondary"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # If we have user data from KeyAuth, display it
        if hasattr(self, 'keyauth') and self.keyauth.get_user_data():
            user_data = self.keyauth.get_user_data()
            user_label = tk.Label(
                header,
                text=f"License: {user_data.get('subscription', 'Unknown')} | Expires: {user_data.get('expires', 'Unknown')}",
                bg=COLORS["background_secondary"],
                fg=COLORS["text_muted"]
            )
            user_label.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Create tab control
        self.tab_control = ttk.Notebook(self.main_container)
        
        # Create tabs
        self.dupe_tab = tk.Frame(self.tab_control, bg=COLORS["background"])
        self.settings_tab = tk.Frame(self.tab_control, bg=COLORS["background"])
        self.logs_tab = tk.Frame(self.tab_control, bg=COLORS["background"])
        
        self.tab_control.add(self.dupe_tab, text="Duplication")
        self.tab_control.add(self.settings_tab, text="Settings")
        self.tab_control.add(self.logs_tab, text="Logs")
        
        self.tab_control.pack(expand=1, fill=tk.BOTH, padx=10, pady=10)
        
        # Setup each tab
        self.setup_dupe_tab()
        self.setup_settings_tab()
        self.setup_logs_tab()
    
    def create_section(self, parent, title):
        """Create a section with a title frame and content frame"""
        section_frame = tk.Frame(parent, bg=COLORS["background"])
        
        # Title frame
        title_frame = tk.Frame(section_frame, bg=COLORS["background_secondary"])
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Arial", 12, "bold"),
            bg=COLORS["background_secondary"],
            fg=COLORS["text_bright"],
            anchor="w"
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Content frame
        content_frame = tk.Frame(section_frame, bg=COLORS["background"], padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        return section_frame, content_frame
    
    def setup_dupe_tab(self):
        """Set up the duplication tab"""
        # Main container
        dupe_container = tk.Frame(self.dupe_tab, bg=COLORS["background"], padx=20, pady=20)
        dupe_container.pack(fill=tk.BOTH, expand=True)
        
        # Left and right frames
        left_frame = tk.Frame(dupe_container, bg=COLORS["background"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(dupe_container, bg=COLORS["background"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Game selection section
        game_section, game_content = self.create_section(left_frame, "Game Selection")
        game_section.pack(fill=tk.X, pady=(0, 15))
        
        # Game dropdown
        game_label = tk.Label(
            game_content,
            text="Game:",
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        game_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.game_var = tk.StringVar()
        self.game_var.set(list(GAME_DATA.keys())[0])  # Default to first game
        
        game_dropdown = ttk.Combobox(
            game_content,
            textvariable=self.game_var,
            values=list(GAME_DATA.keys()),
            state="readonly",
            width=25
        )
        game_dropdown.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        # Quest dropdown
        quest_label = tk.Label(
            game_content,
            text="Quest:",
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        quest_label.grid(row=1, column=0, sticky="w", pady=(5, 5))
        
        self.quest_var = tk.StringVar()
        
        quest_dropdown = ttk.Combobox(
            game_content,
            textvariable=self.quest_var,
            values=GAME_DATA[self.game_var.get()]["quests"],
            state="readonly",
            width=25
        )
        quest_dropdown.grid(row=1, column=1, sticky="w", pady=(5, 5))
        
        # Update quest list when game changes
        def update_quest_list(*args):
            quest_dropdown["values"] = GAME_DATA[self.game_var.get()]["quests"]
            self.quest_var.set(GAME_DATA[self.game_var.get()]["quests"][0])
            self.update_item_list()
        
        self.game_var.trace("w", update_quest_list)
        update_quest_list()  # Initialize with default values
        
        # Save file selection
        save_label = tk.Label(
            game_content,
            text="Save File:",
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        save_label.grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        save_frame = tk.Frame(game_content, bg=COLORS["background"])
        save_frame.grid(row=2, column=1, sticky="w", pady=(5, 0))
        
        self.save_var = tk.StringVar()
        
        save_entry = tk.Entry(
            save_frame,
            textvariable=self.save_var,
            width=20,
            bg=COLORS["input_bg"],
            fg=COLORS["text_bright"],
            insertbackground=COLORS["text_bright"],
            relief=tk.FLAT,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        save_entry.pack(side=tk.LEFT)
        
        browse_button = tk.Button(
            save_frame,
            text="Browse",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            activebackground=COLORS["background"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            command=self.browse_save_file
        )
        browse_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Item configuration section
        item_section, item_content = self.create_section(left_frame, "Item Configuration")
        item_section.pack(fill=tk.BOTH, expand=True)
        
        # Item selection
        item_label = tk.Label(
            item_content,
            text="Item:",
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        item_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.item_var = tk.StringVar()
        
        item_dropdown = ttk.Combobox(
            item_content,
            textvariable=self.item_var,
            values=GAME_DATA[self.game_var.get()]["items"],
            state="readonly",
            width=25
        )
        item_dropdown.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        # Quantity selection
        quantity_label = tk.Label(
            item_content,
            text="Quantity:",
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        quantity_label.grid(row=1, column=0, sticky="w", pady=(5, 5))
        
        self.quantity_var = tk.IntVar()
        self.quantity_var.set(10)  # Default quantity
        
        quantity_frame = tk.Frame(item_content, bg=COLORS["background"])
        quantity_frame.grid(row=1, column=1, sticky="w", pady=(5, 5))
        
        quantity_scale = ttk.Scale(
            quantity_frame,
            from_=1,
            to=99,
            orient=tk.HORIZONTAL,
            length=150,
            variable=self.quantity_var
        )
        quantity_scale.pack(side=tk.LEFT)
        
        quantity_display = tk.Label(
            quantity_frame,
            textvariable=self.quantity_var,
            width=3,
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        quantity_display.pack(side=tk.LEFT, padx=(5, 0))
        
        # Update quantity label when scale changes
        def update_quantity_label(*args):
            self.quantity_var.set(int(self.quantity_var.get()))
        
        self.quantity_var.trace("w", update_quantity_label)
        
        # Duplication method section
        method_section, method_content = self.create_section(right_frame, "Duplication Method")
        method_section.pack(fill=tk.X, pady=(0, 15))
        
        # Method selection
        self.method_var = tk.StringVar(value="error277")
        
        error277_radio = tk.Radiobutton(
            method_content,
            text="Error Code 277 Method",
            variable=self.method_var,
            value="error277",
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"]
        )
        error277_radio.pack(anchor=tk.W, pady=(0, 5))
        
        cloud_save_radio = tk.Radiobutton(
            method_content,
            text="Cloud Save Method (Slower but safer)",
            variable=self.method_var,
            value="cloud_save",
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            state=tk.DISABLED  # Disabled for demo
        )
        cloud_save_radio.pack(anchor=tk.W, pady=(0, 5))
        
        save_backup_radio = tk.Radiobutton(
            method_content,
            text="Save Backup Method (Fastest, less stable)",
            variable=self.method_var,
            value="save_backup",
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            state=tk.DISABLED  # Disabled for demo
        )
        save_backup_radio.pack(anchor=tk.W, pady=(0, 5))
        
        # Method description
        method_desc = tk.Label(
            method_content,
            text="The Error Code 277 method uses network manipulation to trick the game\ninto duplicating items while maintaining save integrity.",
            justify=tk.LEFT,
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        method_desc.pack(anchor=tk.W, pady=(5, 0))
        
        # Operation status section
        status_section, status_content = self.create_section(right_frame, "Operation Status")
        status_section.pack(fill=tk.BOTH, expand=True)
        
        # Status indicators
        self.status_var = tk.StringVar(value="Ready")
        
        status_frame = tk.Frame(status_content, bg=COLORS["background"])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_label = tk.Label(
            status_frame,
            text="Status:",
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        status_label.pack(side=tk.LEFT)
        
        status_display = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=COLORS["background"],
            fg=COLORS["success"]
        )
        status_display.pack(side=tk.LEFT, padx=(5, 0))
        
        # Progress bar
        progress_frame = tk.Frame(status_content, bg=COLORS["background"])
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            mode="determinate",
            length=300
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Current operation
        operation_frame = tk.Frame(status_content, bg=COLORS["background"])
        operation_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.operation_var = tk.StringVar(value="")
        
        operation_label = tk.Label(
            operation_frame,
            textvariable=self.operation_var,
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        operation_label.pack(anchor=tk.W)
        
        # Action buttons
        button_frame = tk.Frame(status_content, bg=COLORS["background"])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_button = tk.Button(
            button_frame,
            text="Start Duplication",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.start_duplication
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            bg=COLORS["danger"],
            fg=COLORS["text_bright"],
            activebackground="#d04040",
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=15,
            pady=8,
            state=tk.DISABLED,
            command=self.stop_duplication
        )
        self.stop_button.pack(side=tk.LEFT)
    
    def update_item_list(self, *args):
        """Update item list based on selected game"""
        game = self.game_var.get()
        item_dropdown = self.dupe_tab.nametowidget(
            self.dupe_tab.winfo_children()[0]
                .winfo_children()[0]  # left_frame
                .winfo_children()[1]  # item_section
                .winfo_children()[1]  # content_frame
                .winfo_children()[2]  # item_dropdown
        )
        
        item_dropdown["values"] = GAME_DATA[game]["items"]
        self.item_var.set(GAME_DATA[game]["items"][0])
    
    def browse_save_file(self):
        """Open file browser to select a save file"""
        file_path = filedialog.askopenfilename(
            title="Select Save File",
            filetypes=[
                ("Save Files", "*.sav *.sl2 *.bin"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.save_var.set(file_path)
    
    def setup_settings_tab(self):
        """Set up the settings tab"""
        # Main container
        settings_container = tk.Frame(self.settings_tab, bg=COLORS["background"], padx=20, pady=20)
        settings_container.pack(fill=tk.BOTH, expand=True)
        
        # Settings section
        settings_section, settings_content = self.create_section(settings_container, "Application Settings")
        settings_section.pack(fill=tk.X, pady=(0, 15))
        
        # Auto-save setting
        self.auto_save_var = tk.BooleanVar(value=self.settings.get("auto_save", True))
        
        auto_save_check = tk.Checkbutton(
            settings_content,
            text="Automatically save after duplication",
            variable=self.auto_save_var,
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            activebackground=COLORS["background"],
            activeforeground=COLORS["text"]
        )
        auto_save_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Auto-backup setting
        self.auto_backup_var = tk.BooleanVar(value=self.settings.get("auto_backup", True))
        
        auto_backup_check = tk.Checkbutton(
            settings_content,
            text="Create backup before modifying save files",
            variable=self.auto_backup_var,
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            activebackground=COLORS["background"],
            activeforeground=COLORS["text"]
        )
        auto_backup_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Show popups setting
        self.show_popups_var = tk.BooleanVar(value=self.settings.get("show_popups", True))
        
        show_popups_check = tk.Checkbutton(
            settings_content,
            text="Show popup notifications",
            variable=self.show_popups_var,
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            activebackground=COLORS["background"],
            activeforeground=COLORS["text"]
        )
        show_popups_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Dark mode setting
        self.dark_mode_var = tk.BooleanVar(value=self.settings.get("dark_mode", True))
        
        dark_mode_check = tk.Checkbutton(
            settings_content,
            text="Dark mode (requires restart)",
            variable=self.dark_mode_var,
            bg=COLORS["background"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            activebackground=COLORS["background"],
            activeforeground=COLORS["text"]
        )
        dark_mode_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Animation speed setting
        speed_frame = tk.Frame(settings_content, bg=COLORS["background"])
        speed_frame.pack(fill=tk.X, pady=(5, 0))
        
        speed_label = tk.Label(
            speed_frame,
            text="Animation Speed:",
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        speed_label.pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=self.settings.get("animation_speed", 5))
        
        speed_scale = ttk.Scale(
            speed_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            length=150,
            variable=self.speed_var
        )
        speed_scale.pack(side=tk.LEFT, padx=(10, 5))
        
        speed_display = tk.Label(
            speed_frame,
            textvariable=self.speed_var,
            width=2,
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        speed_display.pack(side=tk.LEFT)
        
        # Update speed label when scale changes
        def update_speed_label(*args):
            self.speed_var.set(int(self.speed_var.get()))
        
        self.speed_var.trace("w", update_speed_label)
        
        # Action buttons
        button_frame = tk.Frame(settings_content, bg=COLORS["background"], pady=15)
        button_frame.pack(fill=tk.X)
        
        save_settings_button = tk.Button(
            button_frame,
            text="Save Settings",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.save_settings
        )
        save_settings_button.pack(side=tk.LEFT, padx=(0, 5))
        
        reset_settings_button = tk.Button(
            button_frame,
            text="Reset to Default",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.reset_settings
        )
        reset_settings_button.pack(side=tk.LEFT)
        
        # License information section
        license_section, license_content = self.create_section(settings_container, "License Information")
        license_section.pack(fill=tk.X, pady=(15, 0))
        
        # If we have user data from KeyAuth, display it
        if hasattr(self, 'keyauth') and self.keyauth.get_user_data():
            user_data = self.keyauth.get_user_data()
            
            # Username
            username_frame = tk.Frame(license_content, bg=COLORS["background"])
            username_frame.pack(fill=tk.X, pady=(0, 5))
            
            username_label = tk.Label(
                username_frame,
                text="Username:",
                width=15,
                anchor="w",
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
            username_label.pack(side=tk.LEFT)
            
            username_value = tk.Label(
                username_frame,
                text=user_data.get("username", "N/A"),
                bg=COLORS["background"],
                fg=COLORS["text_bright"]
            )
            username_value.pack(side=tk.LEFT)
            
            # License type
            license_frame = tk.Frame(license_content, bg=COLORS["background"])
            license_frame.pack(fill=tk.X, pady=(0, 5))
            
            license_label = tk.Label(
                license_frame,
                text="License Type:",
                width=15,
                anchor="w",
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
            license_label.pack(side=tk.LEFT)
            
            license_value = tk.Label(
                license_frame,
                text=user_data.get("subscription", "N/A"),
                bg=COLORS["background"],
                fg=COLORS["text_bright"]
            )
            license_value.pack(side=tk.LEFT)
            
            # Expiry date
            expiry_frame = tk.Frame(license_content, bg=COLORS["background"])
            expiry_frame.pack(fill=tk.X, pady=(0, 5))
            
            expiry_label = tk.Label(
                expiry_frame,
                text="Expires On:",
                width=15,
                anchor="w",
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
            expiry_label.pack(side=tk.LEFT)
            
            expiry_value = tk.Label(
                expiry_frame,
                text=user_data.get("expires", "N/A"),
                bg=COLORS["background"],
                fg=COLORS["text_bright"]
            )
            expiry_value.pack(side=tk.LEFT)
            
            # Last login
            last_login_frame = tk.Frame(license_content, bg=COLORS["background"])
            last_login_frame.pack(fill=tk.X, pady=(0, 5))
            
            last_login_label = tk.Label(
                last_login_frame,
                text="Last Login:",
                width=15,
                anchor="w",
                bg=COLORS["background"],
                fg=COLORS["text"]
            )
            last_login_label.pack(side=tk.LEFT)
            
            last_login_value = tk.Label(
                last_login_frame,
                text=user_data.get("lastlogin", "N/A"),
                bg=COLORS["background"],
                fg=COLORS["text_bright"]
            )
            last_login_value.pack(side=tk.LEFT)
        else:
            # No user data available
            no_data_label = tk.Label(
                license_content,
                text="License information not available",
                bg=COLORS["background"],
                fg=COLORS["text_muted"]
            )
            no_data_label.pack(anchor=tk.W, pady=5)
    
    def save_settings(self):
        """Save the current settings"""
        self.settings = {
            "auto_save": self.auto_save_var.get(),
            "auto_backup": self.auto_backup_var.get(),
            "show_popups": self.show_popups_var.get(),
            "dark_mode": self.dark_mode_var.get(),
            "animation_speed": self.speed_var.get()
        }
        
        # Save to file
        try:
            settings_dir = os.path.join(os.path.dirname(__file__), "..", "settings")
            os.makedirs(settings_dir, exist_ok=True)
            
            settings_file = os.path.join(settings_dir, "settings.json")
            with open(settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
            
            messagebox.showinfo("Settings", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        default_settings = {
            "auto_save": True,
            "auto_backup": True,
            "show_popups": True,
            "dark_mode": True,
            "animation_speed": 5
        }
        
        # Update variables
        self.auto_save_var.set(default_settings["auto_save"])
        self.auto_backup_var.set(default_settings["auto_backup"])
        self.show_popups_var.set(default_settings["show_popups"])
        self.dark_mode_var.set(default_settings["dark_mode"])
        self.speed_var.set(default_settings["animation_speed"])
        
        # Update settings
        self.settings = default_settings
        
        messagebox.showinfo("Settings", "Settings reset to defaults")
    
    def setup_logs_tab(self):
        """Set up the logs tab"""
        # Main container
        logs_container = tk.Frame(self.logs_tab, bg=COLORS["background"], padx=20, pady=20)
        logs_container.pack(fill=tk.BOTH, expand=True)
        
        # Logs section
        logs_section, logs_content = self.create_section(logs_container, "Operation Logs")
        logs_section.pack(fill=tk.BOTH, expand=True)
        
        # Log display
        log_frame = tk.Frame(logs_content, bg=COLORS["background"])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable text widget
        self.log_text = tk.Text(
            log_frame,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Add some initial content
        self.log_operation("Application started")
        self.log_operation("Authentication successful")
        
        # Action buttons
        button_frame = tk.Frame(logs_content, bg=COLORS["background"], pady=15)
        button_frame.pack(fill=tk.X)
        
        refresh_button = tk.Button(
            button_frame,
            text="Refresh Logs",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.refresh_logs
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_button = tk.Button(
            button_frame,
            text="Clear Logs",
            bg=COLORS["danger"],
            fg=COLORS["text_bright"],
            activebackground="#d04040",
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.clear_logs
        )
        clear_button.pack(side=tk.LEFT)
    
    def log_operation(self, message):
        """Add an operation to the log"""
        # Get current time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format log entry
        log_entry = f"[{timestamp}] {message}\n"
        
        # Add to text widget
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Also log to file
        try:
            logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            log_file = os.path.join(logs_dir, f"runeslayer_{datetime.now().strftime('%Y%m%d')}.log")
            with open(log_file, "a") as f:
                f.write(log_entry)
        except:
            # Silently fail if we can't write to the log file
            pass
        
        # If we have KeyAuth, also log there
        if hasattr(self, 'keyauth'):
            self.keyauth.log(message)
    
    def refresh_logs(self):
        """Refresh the logs display"""
        # For demo purposes, just add a refresh message
        self.log_operation("Logs refreshed")
    
    def clear_logs(self):
        """Clear the logs display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.log_operation("Logs cleared")
    
    def start_duplication(self):
        """Start the duplication process"""
        # Get values
        game = self.game_var.get()
        quest = self.quest_var.get()
        save_file = self.save_var.get()
        item = self.item_var.get()
        quantity = self.quantity_var.get()
        
        # Validate inputs
        if not save_file:
            messagebox.showerror("Error", "Please select a save file")
            return
        
        if not item:
            messagebox.showerror("Error", "Please select an item to duplicate")
            return
        
        # Disabled for demo: Actual save file check
        """
        if not os.path.exists(save_file):
            messagebox.showerror("Error", "Save file not found.")
            return
        """
        
        # Update UI
        self.status_var.set("Running")
        self.operation_var.set("Initializing...")
        self.progress_var.set(0)
        
        # Disable start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Set flags
        self.duplication_running = True
        self.stop_duplication_flag = False
        
        # Log the operation
        self.log_operation(f"Starting duplication: {quantity}x {item} in {game} ({quest})")
        
        # Run in a separate thread
        threading.Thread(
            target=self.run_duplication_process,
            args=(game, quest, save_file, item, quantity),
            daemon=True
        ).start()
    
    def run_duplication_process(self, game, quest, save_file, item, quantity):
        """Run the duplication process in a separate thread"""
        try:
            # Steps in the process
            steps = [
                "Analyzing save file",
                "Locating item data",
                "Preparing Error 277 method",
                "Creating backup",
                "Executing network disruption",
                "Injecting duplicated data",
                "Verifying item count",
                "Finalizing and saving"
            ]
            
            # Simulate each step
            for i, step in enumerate(steps):
                if self.stop_duplication_flag:
                    # Handle stopped duplication
                    self.root.after(0, self.handle_stopped_duplication)
                    return
                
                # Update progress (in main thread)
                progress = (i / len(steps)) * 100
                self.root.after(0, lambda p=progress, s=step: self.update_progress(p, s))
                
                # Log step
                self.root.after(0, lambda s=step: self.log_operation(s))
                
                # For step 4, show the Error 277 dialog
                if i == 4:
                    self.root.after(0, self.show_error_277_dialog)
                
                # Simulate processing time
                time.sleep(1 + random.random() * 2)  # 1-3 seconds per step
            
            # Duplication complete
            if not self.stop_duplication_flag:
                self.root.after(0, lambda: self.complete_duplication(item, quantity))
        
        except Exception as e:
            # Handle error
            self.root.after(0, lambda: self.handle_duplication_error(str(e)))
    
    def update_progress(self, progress, step):
        """Update progress UI - called from main thread"""
        self.progress_var.set(progress)
        self.operation_var.set(step)
    
    def complete_duplication(self, item, quantity):
        """Complete the duplication process - called from main thread"""
        # Update UI
        self.status_var.set("Completed")
        self.operation_var.set(f"Successfully duplicated {quantity}x {item}")
        self.progress_var.set(100)
        
        # Log completion
        self.log_operation(f"Duplication completed: {quantity}x {item} added to inventory")
        
        # Show success message
        if self.settings.get("show_popups", True):
            messagebox.showinfo(
                "Duplication Complete",
                f"Successfully duplicated {quantity}x {item}"
            )
        
        # Reset UI
        self.reset_duplication_ui()
    
    def handle_stopped_duplication(self):
        """Handle stopped duplication - called from main thread"""
        # Update UI
        self.status_var.set("Stopped")
        self.operation_var.set("Duplication process stopped by user")
        
        # Log
        self.log_operation("Duplication process stopped by user")
        
        # Reset UI
        self.reset_duplication_ui()
    
    def handle_duplication_error(self, error_msg):
        """Handle duplication error - called from main thread"""
        # Update UI
        self.status_var.set("Error")
        self.operation_var.set(f"Error: {error_msg}")
        
        # Log error
        self.log_operation(f"Duplication failed: {error_msg}")
        
        # Show error message
        messagebox.showerror(
            "Duplication Error",
            f"An error occurred during the duplication process:\n\n{error_msg}"
        )
        
        # Reset UI
        self.reset_duplication_ui()
    
    def reset_duplication_ui(self):
        """Reset the UI after duplication completes, stops, or errors"""
        # Reset flags
        self.duplication_running = False
        self.stop_duplication_flag = False
        
        # Enable start button, disable stop button
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def execute_step(self, step_name, item, quantity):
        """Execute a specific step in the Error Code 277 method"""
        # In a real implementation, this would handle the actual duplication logic
        # For this demo, we're just simulating the process
        self.log_operation(f"Executing step: {step_name}")
        
        # Simulate step execution time
        time.sleep(1 + random.random())
    
    def show_error_277_dialog(self):
        """Show a simulated Error Code 277 dialog"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Disconnected")
        dialog.geometry("400x200")
        dialog.configure(bg="#36393F")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Dialog content
        content_frame = tk.Frame(dialog, bg="#36393F")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            content_frame,
            text="Disconnected",
            font=("Arial", 16, "bold"),
            bg="#36393F",
            fg="#FFFFFF"
        )
        title_label.pack(pady=(0, 10))
        
        # Separator
        separator = ttk.Separator(content_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)
        
        message_label = tk.Label(
            content_frame,
            text="Lost connection to the game server, please reconnect\n(Error Code: 277)",
            bg="#36393F",
            fg="#DCDDDE",
            justify=tk.CENTER
        )
        message_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg="#36393F")
        button_frame.pack(pady=(10, 0))
        
        leave_button = tk.Button(
            button_frame,
            text="Leave",
            bg="#36393F",
            fg="#DCDDDE",
            activebackground="#2F3136",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            width=12,
            padx=10,
            pady=5
        )
        leave_button.pack(side=tk.LEFT, padx=(0, 10))
        
        reconnect_button = tk.Button(
            button_frame,
            text="Reconnect",
            bg="#FFFFFF",
            fg="#36393F",
            activebackground="#CCCCCC",
            activeforeground="#36393F",
            relief=tk.FLAT,
            width=12,
            padx=10,
            pady=5
        )
        reconnect_button.pack(side=tk.LEFT)
        
        # Auto-dismiss dialog after a delay
        def close_dialog():
            dialog.destroy()
            # Simulate reconnection progress
            progress_dialog = tk.Toplevel(self.root)
            progress_dialog.title("Reconnecting")
            progress_dialog.geometry("300x100")
            progress_dialog.configure(bg="#36393F")
            progress_dialog.transient(self.root)
            progress_dialog.grab_set()
            
            # Center dialog
            progress_dialog.update_idletasks()
            width = progress_dialog.winfo_width()
            height = progress_dialog.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            progress_dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            # Progress content
            progress_frame = tk.Frame(progress_dialog, bg="#36393F")
            progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            progress_label = tk.Label(
                progress_frame,
                text="Reconnecting to server...",
                bg="#36393F",
                fg="#FFFFFF"
            )
            progress_label.pack(pady=(0, 10))
            
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(
                progress_frame,
                variable=progress_var,
                mode="determinate",
                length=250
            )
            progress_bar.pack()
            
            # Simulate progress
            def update_progress(value):
                progress_var.set(value)
                if value < 100:
                    progress_dialog.after(50, lambda: update_progress(value + 2))
                else:
                    progress_dialog.after(500, progress_dialog.destroy)
            
            update_progress(0)
        
        # Set button commands
        leave_button.config(command=close_dialog)
        reconnect_button.config(command=close_dialog)
        
        # Auto-close after 3 seconds if user doesn't interact
        dialog.after(3000, close_dialog)
    
    def stop_duplication(self):
        """Stop the duplication process"""
        self.stop_duplication_flag = True
        self.stop_button.config(state=tk.DISABLED)
        self.operation_var.set("Stopping...")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = RuneSlayerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
