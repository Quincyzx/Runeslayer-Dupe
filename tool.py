#!/usr/bin/env python3
"""
RuneSlayer Tool - Main Application
This file handles authentication and provides the main tool functionality.
"""
import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import random
import requests
import base64
import uuid

# Game titles
GAMES = ["Elden Ring", "Dark Souls 3", "Skyrim", "Fallout 4", "The Witcher 3"]

# Items per game
ITEMS = {
    "Elden Ring": ["Moonveil Katana", "Rivers of Blood", "Sacred Relic Sword", "Rune Stack", "Starlight Shard"],
    "Dark Souls 3": ["Souls Stack", "Ember", "Titanite Slab", "Farron Greatsword", "Wolf Knight Greatsword"],
    "Skyrim": ["Gold", "Dragon Bones", "Daedric Armor", "Black Soul Gem", "Ebony Ingot"],
    "Fallout 4": ["Nuka Cola", "Fusion Core", "Stimpak", "Quantum", "Bottle Caps"],
    "The Witcher 3": ["Crowns", "Dimeritium Ingot", "Meteorite Silver", "White Gull", "Crafting Diagram"]
}

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
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        self.root.configure(bg=COLORS["background"])
        
        # Default user info if none provided
        if user_info is None:
            self.user_info = {"key": "UNKNOWN", "uses_remaining": 0}
        else:
            self.user_info = user_info
        
        # Set window icon (if available)
        self.set_window_icon()
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Variables
        self.selected_game = tk.StringVar()
        self.selected_item = tk.StringVar()
        self.quantity = tk.IntVar()
        self.quantity.set(1)
        self.save_file_path = tk.StringVar()
        self.is_duplicating = False
        self.stop_requested = False
        
        # Log file setup
        self.log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runeslayer.log")
        
        # Setup UI
        self.setup_ui()
        
        # Log startup
        key = self.user_info.get('key', 'UNKNOWN')
        truncated_key = key[:8] + "..." if len(key) > 8 else key
        uses = self.user_info.get('uses_remaining', 0)
        self.log_operation(f"RuneSlayer started with license key {truncated_key} ({uses} uses remaining)")
    
    def set_window_icon(self):
        """Set the window icon if available"""
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
            except:
                pass
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header frame
        header_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="RuneSlayer",
            font=("Arial", 24, "bold"),
            bg=COLORS["background"],
            fg=COLORS["text_bright"]
        )
        title_label.pack(side=tk.LEFT)
        
        # User info
        user_frame = tk.Frame(header_frame, bg=COLORS["background"])
        user_frame.pack(side=tk.RIGHT)
        
        # Key info (truncated for security)
        key = self.user_info.get('key', 'UNKNOWN')
        truncated_key = key[:10] + "..." if len(key) > 10 else key
        
        key_label = tk.Label(
            user_frame,
            text=f"Key: {truncated_key}",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        key_label.pack(anchor=tk.E)
        
        # Uses remaining
        uses_label = tk.Label(
            user_frame,
            text=f"Uses remaining: {self.user_info.get('uses_remaining', 0)}",
            font=("Arial", 10),
            bg=COLORS["background"],
            fg=COLORS["primary"]
        )
        uses_label.pack(anchor=tk.E)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1 - Duplication
        self.dupe_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dupe_tab, text="Item Duplication")
        self.setup_dupe_tab()
        
        # Tab 2 - Settings
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        self.setup_settings_tab()
        
        # Tab 3 - Logs
        self.logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_tab, text="Logs")
        self.setup_logs_tab()
        
        # Footer frame
        footer_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        version_label = tk.Label(
            footer_frame,
            text="v1.0",
            font=("Arial", 8),
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        version_label.pack(side=tk.LEFT)
        
        exit_btn = tk.Button(
            footer_frame,
            text="Exit",
            bg=COLORS["danger"],
            fg=COLORS["text_bright"],
            activebackground="#d04040",
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.root.destroy
        )
        exit_btn.pack(side=tk.RIGHT)
    
    def create_section(self, parent, title):
        """Create a section with a title frame and content frame"""
        # Container frame
        container = tk.Frame(parent, bg=COLORS["background"])
        container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Title frame
        title_frame = tk.Frame(container, bg=COLORS["primary"], height=30)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Arial", 12, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            padx=10,
            pady=5
        )
        title_label.pack(anchor=tk.W)
        
        # Content frame
        content_frame = tk.Frame(container, bg=COLORS["background_secondary"], padx=15, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        return content_frame
    
    def setup_dupe_tab(self):
        """Set up the duplication tab"""
        # Split into left and right frames
        left_frame = tk.Frame(self.dupe_tab, bg=COLORS["background"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = tk.Frame(self.dupe_tab, bg=COLORS["background"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Game Selection Section
        game_section = self.create_section(left_frame, "Game Selection")
        
        game_label = tk.Label(
            game_section,
            text="Select Game:",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        game_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Game dropdown
        game_dropdown = ttk.Combobox(
            game_section,
            textvariable=self.selected_game,
            values=GAMES,
            state="readonly",
            width=20
        )
        game_dropdown.pack(anchor=tk.W, pady=(0, 10))
        game_dropdown.current(0)
        
        # Item Selection Section
        item_section = self.create_section(left_frame, "Item Selection")
        
        item_label = tk.Label(
            item_section,
            text="Select Item:",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        item_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Create Listbox for items
        item_frame = tk.Frame(item_section, bg=COLORS["background_secondary"])
        item_frame.pack(fill=tk.BOTH, expand=True)
        
        self.item_listbox = tk.Listbox(
            item_frame,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            selectbackground=COLORS["primary"],
            selectforeground=COLORS["text_bright"],
            height=10,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"]
        )
        self.item_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar to listbox
        item_scrollbar = tk.Scrollbar(item_frame, orient=tk.VERTICAL)
        item_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Link scrollbar and listbox
        self.item_listbox.config(yscrollcommand=item_scrollbar.set)
        item_scrollbar.config(command=self.item_listbox.yview)
        
        # Fill listbox with initial items
        self.update_item_list()
        
        # Save File Selection Section
        save_section = self.create_section(right_frame, "Save File")
        
        save_label = tk.Label(
            save_section,
            text="Save File Path:",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        save_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Save file path entry and browse button
        save_frame = tk.Frame(save_section, bg=COLORS["background_secondary"])
        save_frame.pack(fill=tk.X)
        
        save_entry = tk.Entry(
            save_frame,
            textvariable=self.save_file_path,
            width=30,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = tk.Button(
            save_frame,
            text="Browse",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=10,
            pady=2,
            command=self.browse_save_file
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Duplication Options Section
        options_section = self.create_section(right_frame, "Duplication Options")
        
        # Quantity
        quantity_frame = tk.Frame(options_section, bg=COLORS["background_secondary"])
        quantity_frame.pack(fill=tk.X, pady=(0, 10))
        
        quantity_label = tk.Label(
            quantity_frame,
            text="Quantity:",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        quantity_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Decrease button
        dec_btn = tk.Button(
            quantity_frame,
            text="-",
            width=2,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            command=lambda: self.adjust_quantity(-1)
        )
        dec_btn.pack(side=tk.LEFT)
        
        # Quantity display
        self.quantity_value_label = tk.Label(
            quantity_frame,
            textvariable=self.quantity,
            width=5,
            bg=COLORS["input_bg"],
            fg=COLORS["text_bright"]
        )
        self.quantity_value_label.pack(side=tk.LEFT, padx=1)
        
        # Increase button
        inc_btn = tk.Button(
            quantity_frame,
            text="+",
            width=2,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            command=lambda: self.adjust_quantity(1)
        )
        inc_btn.pack(side=tk.LEFT)
        
        # Multiple of 10 buttons
        btn_frame = tk.Frame(options_section, bg=COLORS["background_secondary"])
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        x10_btn = tk.Button(
            btn_frame,
            text="×10",
            width=5,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            command=lambda: self.set_quantity(10)
        )
        x10_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        x50_btn = tk.Button(
            btn_frame,
            text="×50",
            width=5,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            command=lambda: self.set_quantity(50)
        )
        x50_btn.pack(side=tk.LEFT, padx=5)
        
        x100_btn = tk.Button(
            btn_frame,
            text="×100",
            width=5,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            command=lambda: self.set_quantity(100)
        )
        x100_btn.pack(side=tk.LEFT, padx=5)
        
        x999_btn = tk.Button(
            btn_frame,
            text="×999",
            width=5,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            command=lambda: self.set_quantity(999)
        )
        x999_btn.pack(side=tk.LEFT, padx=5)
        
        # Method selection
        method_label = tk.Label(
            options_section,
            text="Duplication Method:",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        method_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.method_var = tk.StringVar()
        self.method_var.set("Save Backup Method")
        
        method_radio1 = tk.Radiobutton(
            options_section,
            text="Save Backup Method",
            variable=self.method_var,
            value="Save Backup Method",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            activebackground=COLORS["background_secondary"],
            activeforeground=COLORS["text_bright"]
        )
        method_radio1.pack(anchor=tk.W)
        
        method_radio2 = tk.Radiobutton(
            options_section,
            text="Error Code 277 Method",
            variable=self.method_var,
            value="Error Code 277 Method",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            activebackground=COLORS["background_secondary"],
            activeforeground=COLORS["text_bright"]
        )
        method_radio2.pack(anchor=tk.W)
        
        # Action buttons
        action_frame = tk.Frame(right_frame, bg=COLORS["background"])
        action_frame.pack(fill=tk.X, pady=10)
        
        # Start button
        self.start_btn = tk.Button(
            action_frame,
            text="Start Duplication",
            bg=COLORS["success"],
            fg=COLORS["text_bright"],
            activebackground="#3ca374",
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=10,
            pady=8,
            command=self.start_duplication
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = tk.Button(
            action_frame,
            text="Stop",
            bg=COLORS["danger"],
            fg=COLORS["text_bright"],
            activebackground="#d04040",
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=10,
            pady=8,
            command=self.stop_duplication,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        # Progress section
        progress_section = self.create_section(right_frame, "Progress")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_var.set(0)
        
        self.progress_bar = ttk.Progressbar(
            progress_section,
            variable=self.progress_var,
            maximum=100,
            length=300,
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to duplicate items")
        
        status_label = tk.Label(
            progress_section,
            textvariable=self.status_var,
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            wraplength=300,
            justify=tk.LEFT
        )
        status_label.pack(fill=tk.X)
        
        # Bind events
        game_dropdown.bind("<<ComboboxSelected>>", self.update_item_list)
        self.item_listbox.bind("<<ListboxSelect>>", self.on_item_select)
    
    def update_item_list(self, *args):
        """Update item list based on selected game"""
        game = self.selected_game.get()
        
        # Clear the listbox
        self.item_listbox.delete(0, tk.END)
        
        # Get items for the selected game
        items = ITEMS.get(game, [])
        
        # Add items to the listbox
        for item in items:
            self.item_listbox.insert(tk.END, item)
        
        # Select the first item by default
        if items:
            self.item_listbox.selection_set(0)
            self.selected_item.set(items[0])
    
    def on_item_select(self, event):
        """Handle item selection from listbox"""
        selection = self.item_listbox.curselection()
        if selection:
            index = selection[0]
            item = self.item_listbox.get(index)
            self.selected_item.set(item)
    
    def browse_save_file(self):
        """Open file browser to select a save file"""
        file_path = filedialog.askopenfilename(
            title="Select Save File",
            filetypes=[
                ("Save Files", "*.sav *.sl2 *.ess *.fos *.dat"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.save_file_path.set(file_path)
    
    def adjust_quantity(self, delta):
        """Adjust quantity by delta"""
        value = self.quantity.get() + delta
        value = max(1, min(999, value))
        self.quantity.set(value)
    
    def set_quantity(self, value):
        """Set quantity to a specific value"""
        self.quantity.set(value)
    
    def setup_settings_tab(self):
        """Set up the settings tab"""
        # Create container
        settings_frame = tk.Frame(self.settings_tab, bg=COLORS["background"], padx=20, pady=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # General Settings Section
        general_section = self.create_section(settings_frame, "General Settings")
        
        # Backup settings
        backup_frame = tk.Frame(general_section, bg=COLORS["background_secondary"])
        backup_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.backup_var = tk.BooleanVar()
        self.backup_var.set(True)
        
        backup_check = tk.Checkbutton(
            backup_frame,
            text="Create backup of save files before modifying",
            variable=self.backup_var,
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            activebackground=COLORS["background_secondary"],
            activeforeground=COLORS["text_bright"]
        )
        backup_check.pack(anchor=tk.W)
        
        # Theme settings
        theme_frame = tk.Frame(general_section, bg=COLORS["background_secondary"])
        theme_frame.pack(fill=tk.X, pady=(0, 10))
        
        theme_label = tk.Label(
            theme_frame,
            text="Theme:",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        theme_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.theme_var = tk.StringVar()
        self.theme_var.set("Discord Dark")
        
        theme_dropdown = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["Discord Dark", "Light Mode", "Blue Steel"],
            state="readonly",
            width=20
        )
        theme_dropdown.pack(side=tk.LEFT)
        
        # Advanced Settings Section
        advanced_section = self.create_section(settings_frame, "Advanced Settings")
        
        # Default save directory
        save_dir_frame = tk.Frame(advanced_section, bg=COLORS["background_secondary"])
        save_dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        save_dir_label = tk.Label(
            save_dir_frame,
            text="Default Save Directory:",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        save_dir_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.save_dir_var = tk.StringVar()
        
        save_dir_entry = tk.Entry(
            save_dir_frame,
            textvariable=self.save_dir_var,
            width=40,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        save_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_dir_btn = tk.Button(
            save_dir_frame,
            text="Browse",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=10,
            pady=2,
            command=self.browse_save_dir
        )
        browse_dir_btn.pack(side=tk.RIGHT)
        
        # Debug mode
        debug_frame = tk.Frame(advanced_section, bg=COLORS["background_secondary"])
        debug_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.debug_var = tk.BooleanVar()
        self.debug_var.set(False)
        
        debug_check = tk.Checkbutton(
            debug_frame,
            text="Enable debug mode (verbose logging)",
            variable=self.debug_var,
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            selectcolor=COLORS["background_secondary"],
            activebackground=COLORS["background_secondary"],
            activeforeground=COLORS["text_bright"]
        )
        debug_check.pack(anchor=tk.W)
        
        # Action buttons
        action_frame = tk.Frame(settings_frame, bg=COLORS["background"])
        action_frame.pack(fill=tk.X, pady=10)
        
        save_btn = tk.Button(
            action_frame,
            text="Save Settings",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.save_settings
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        reset_btn = tk.Button(
            action_frame,
            text="Reset to Defaults",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.reset_settings
        )
        reset_btn.pack(side=tk.LEFT)
    
    def browse_save_dir(self):
        """Open directory browser to select default save directory"""
        directory = filedialog.askdirectory(title="Select Default Save Directory")
        
        if directory:
            self.save_dir_var.set(directory)
    
    def save_settings(self):
        """Save the current settings"""
        try:
            # Prepare settings dict
            settings = {
                "backup_saves": self.backup_var.get(),
                "theme": self.theme_var.get(),
                "save_directory": self.save_dir_var.get(),
                "debug_mode": self.debug_var.get()
            }
            
            # Save to file
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Settings", "Settings saved successfully")
            self.log_operation("Settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.backup_var.set(True)
        self.theme_var.set("Discord Dark")
        self.save_dir_var.set("")
        self.debug_var.set(False)
        
        messagebox.showinfo("Settings", "Settings reset to defaults")
        self.log_operation("Settings reset to defaults")
    
    def setup_logs_tab(self):
        """Set up the logs tab"""
        # Create container
        logs_frame = tk.Frame(self.logs_tab, bg=COLORS["background"], padx=20, pady=20)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log viewer section
        log_section = self.create_section(logs_frame, "Operation Log")
        
        # Text widget for logs
        log_frame = tk.Frame(log_section, bg=COLORS["background_secondary"])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar to text widget
        log_scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Link scrollbar and text widget
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
        
        # Action buttons
        action_frame = tk.Frame(logs_frame, bg=COLORS["background"])
        action_frame.pack(fill=tk.X, pady=10)
        
        refresh_btn = tk.Button(
            action_frame,
            text="Refresh Logs",
            bg=COLORS["primary"],
            fg=COLORS["text_bright"],
            activebackground=COLORS["primary_hover"],
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.refresh_logs
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(
            action_frame,
            text="Clear Logs",
            bg=COLORS["danger"],
            fg=COLORS["text_bright"],
            activebackground="#d04040",
            activeforeground=COLORS["text_bright"],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.clear_logs
        )
        clear_btn.pack(side=tk.LEFT)
        
        # Load logs
        self.refresh_logs()
    
    def log_operation(self, message):
        """Add an operation to the log"""
        try:
            # Get timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create log entry
            log_entry = f"[{timestamp}] {message}\n"
            
            # Append to log file
            with open(self.log_file, "a") as f:
                f.write(log_entry)
            
            # Update the log text widget if it exists
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
                
        except Exception as e:
            print(f"Error logging operation: {str(e)}")
    
    def refresh_logs(self):
        """Refresh the logs display"""
        # Clear current logs
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        # Try to read log file
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    logs = f.read()
                self.log_text.insert(tk.END, logs)
            else:
                self.log_text.insert(tk.END, "No log file found. Log will be created when operations are performed.\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Error reading log file: {str(e)}\n")
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_logs(self):
        """Clear the logs display"""
        # Ask for confirmation
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            try:
                # Clear the log file
                with open(self.log_file, "w") as f:
                    f.write("")
                
                # Clear the text widget
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, "Logs cleared.\n")
                self.log_text.config(state=tk.DISABLED)
                
                # Log the clearing operation
                self.log_operation("Logs cleared")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {str(e)}")
    
    def start_duplication(self):
        """Start the duplication process"""
        # Get inputs
        game = self.selected_game.get()
        item = self.selected_item.get()
        quantity = self.quantity.get()
        save_file = self.save_file_path.get().strip()
        method = self.method_var.get()
        
        # Validate inputs
        if not game:
            messagebox.showerror("Error", "Please select a game")
            return
        
        if not item:
            messagebox.showerror("Error", "Please select an item")
            return
        
        if not save_file:
            messagebox.showerror("Error", "Please select a save file")
            return
        
        if not os.path.exists(save_file):
            messagebox.showerror("Error", "Save file not found")
            return
        
        # Confirm operation
        if not messagebox.askyesno("Confirm Duplication", f"Start duplication of {quantity}× {item} in {game}?"):
            return
        
        # Update UI
        self.is_duplicating = True
        self.stop_requested = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set(f"Starting duplication of {quantity}× {item}...")
        
        # Log operation
        self.log_operation(f"Started duplication of {quantity}× {item} in {game} using {method}")
        
        # Start in a new thread
        duplication_thread = threading.Thread(
            target=self.run_duplication_process,
            args=(game, save_file, item, quantity, method)
        )
        duplication_thread.daemon = True
        duplication_thread.start()
    
    def run_duplication_process(self, game, save_file, item, quantity, method):
        """Run the duplication process in a separate thread"""
        try:
            # Update progress
            self.update_progress(10, f"Analyzing save file for {game}...")
            time.sleep(1)  # Simulate analysis
            
            if self.stop_requested:
                self.handle_stopped_duplication()
                return
            
            # Create backup
            if self.backup_var.get():
                self.update_progress(20, "Creating backup of save file...")
                time.sleep(1.5)  # Simulate backup creation
                
                if self.stop_requested:
                    self.handle_stopped_duplication()
                    return
            
            # Process steps
            total_steps = 5
            base_progress = 20
            progress_per_step = (90 - base_progress) / total_steps
            
            # Step 1
            self.update_progress(
                base_progress + progress_per_step,
                f"[Step 1/5] Locating {item} pattern in save file..."
            )
            time.sleep(1)  # Simulate work
            
            if self.stop_requested:
                self.handle_stopped_duplication()
                return
            
            # Step 2
            self.update_progress(
                base_progress + 2 * progress_per_step,
                f"[Step 2/5] Decoding save file structure..."
            )
            time.sleep(1.5)  # Simulate work
            
            if self.stop_requested:
                self.handle_stopped_duplication()
                return
            
            # Step 3
            self.update_progress(
                base_progress + 3 * progress_per_step,
                f"[Step 3/5] Preparing duplication sequence..."
            )
            time.sleep(1)  # Simulate work
            
            if self.stop_requested:
                self.handle_stopped_duplication()
                return
            
            # Step 4
            if method == "Error Code 277 Method":
                # Special error method
                self.update_progress(
                    base_progress + 4 * progress_per_step,
                    f"[Step 4/5] Applying Error Code 277 method..."
                )
                
                # Show error dialog on main thread
                self.root.after(0, self.show_error_277_dialog)
                
                # Wait for dialog to be processed
                time.sleep(3)
            else:
                # Standard method
                self.update_progress(
                    base_progress + 4 * progress_per_step,
                    f"[Step 4/5] Injecting duplication code for {quantity}× {item}..."
                )
                time.sleep(2)  # Simulate work
            
            if self.stop_requested:
                self.handle_stopped_duplication()
                return
            
            # Step 5
            self.update_progress(
                base_progress + 5 * progress_per_step,
                f"[Step 5/5] Finalizing changes and verifying save file..."
            )
            time.sleep(1.5)  # Simulate work
            
            if self.stop_requested:
                self.handle_stopped_duplication()
                return
            
            # Complete the duplication
            self.root.after(0, lambda: self.complete_duplication(item, quantity))
            
        except Exception as e:
            error_msg = f"Error during duplication: {str(e)}"
            self.root.after(0, lambda: self.handle_duplication_error(error_msg))
            print(error_msg)
    
    def update_progress(self, progress, step):
        """Update progress UI - called from main thread"""
        self.progress_var.set(progress)
        self.status_var.set(step)
        self.root.update()
    
    def complete_duplication(self, item, quantity):
        """Complete the duplication process - called from main thread"""
        # Update UI
        self.progress_var.set(100)
        self.status_var.set(f"Duplication complete! Added {quantity}× {item} to save file.")
        
        # Log success
        self.log_operation(f"Successfully duplicated {quantity}× {item}")
        
        # Show success message
        messagebox.showinfo(
            "Duplication Complete",
            f"Successfully duplicated {quantity}× {item} to your save file!"
        )
        
        # Reset UI
        self.reset_duplication_ui()
    
    def handle_stopped_duplication(self):
        """Handle stopped duplication - called from main thread"""
        # Log operation
        self.log_operation("Duplication process was stopped by user")
        
        # Update UI
        self.status_var.set("Duplication stopped.")
        
        # Reset UI
        self.root.after(0, self.reset_duplication_ui)
    
    def handle_duplication_error(self, error_msg):
        """Handle duplication error - called from main thread"""
        # Log error
        self.log_operation(f"Duplication error: {error_msg}")
        
        # Show error message
        messagebox.showerror("Duplication Error", error_msg)
        
        # Update UI
        self.status_var.set(f"Error: {error_msg}")
        
        # Reset UI
        self.reset_duplication_ui()
    
    def reset_duplication_ui(self):
        """Reset the UI after duplication completes, stops, or errors"""
        self.is_duplicating = False
        self.stop_requested = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def show_error_277_dialog(self):
        """Show a simulated Error Code 277 dialog"""
        # Create a toplevel window
        error_dialog = tk.Toplevel(self.root)
        error_dialog.title("Error Code 277")
        error_dialog.geometry("400x250")
        error_dialog.resizable(False, False)
        error_dialog.configure(bg=COLORS["background_secondary"])
        
        # Make it modal
        error_dialog.transient(self.root)
        error_dialog.grab_set()
        
        # Center the dialog
        error_dialog.update_idletasks()
        width = error_dialog.winfo_width()
        height = error_dialog.winfo_height()
        x = (error_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (error_dialog.winfo_screenheight() // 2) - (height // 2)
        error_dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Dialog contents
        error_icon = tk.Label(
            error_dialog,
            text="❌",
            font=("Arial", 48),
            bg=COLORS["background_secondary"],
            fg=COLORS["danger"]
        )
        error_icon.pack(pady=(20, 10))
        
        error_title = tk.Label(
            error_dialog,
            text="Error Code 277",
            font=("Arial", 14, "bold"),
            bg=COLORS["background_secondary"],
            fg=COLORS["text_bright"]
        )
        error_title.pack(pady=(0, 10))
        
        error_msg = tk.Label(
            error_dialog,
            text="Save file corruption detected.\nDuplication in progress...",
            bg=COLORS["background_secondary"],
            fg=COLORS["text"]
        )
        error_msg.pack(pady=(0, 20))
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_var.set(0)
        
        progress_bar = ttk.Progressbar(
            error_dialog,
            variable=progress_var,
            maximum=100,
            length=300,
            mode="determinate"
        )
        progress_bar.pack(pady=(0, 10))
        
        # Start a timer to update the progress bar
        def update_progress(value):
            if value <= 100:
                progress_var.set(value)
                error_dialog.after(50, lambda: update_progress(value + 2))
            else:
                error_dialog.destroy()
        
        # Start the progress update
        update_progress(0)
    
    def stop_duplication(self):
        """Stop the duplication process"""
        if self.is_duplicating:
            self.stop_requested = True
            self.status_var.set("Stopping duplication process...")
            self.stop_btn.config(state=tk.DISABLED)

# GitHub Configuration - Must match loader.py
GITHUB_USER = "Quincyzx"        # GitHub username 
GITHUB_REPO = "Runeslayer-Dupe" # GitHub repository name
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
KEYS_FILE_PATH = "keys.json"  # Path to keys file in GitHub repo

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
        # Pre-fill with a test key for development
        self.key_var.set("RUNE-SLAYER-1234-ABCD-5678-EFGH-9101")
        
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
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        try:
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                file_data = response.json()
                sha = file_data.get('sha')
                if sha:
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
        
        # Set up headers
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        data = {
            "message": "Update keys after authentication",
            "content": encoded_content,
            "sha": sha  # Use the retrieved SHA for the update
        }
        
        try:
            response = requests.put(api_url, json=data, headers=headers)
            
            if response.status_code in (200, 201):
                print("Successfully updated keys.json on GitHub.")
                return True
            else:
                print(f"Error updating keys.json on GitHub: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Exception updating keys: {str(e)}")
            return False
    
    def _authenticate_thread(self, license_key):
        """Authentication process in a separate thread"""
        try:
            # Debug output
            print(f"Starting authentication with key: {license_key}")
            
            # Download keys.json from GitHub
            print("Attempting to download keys.json from GitHub...")
            success, result = self.download_file_from_github(KEYS_FILE_PATH)
            
            # If GitHub download fails, show error and return
            if not success:
                print(f"GitHub download failed: {result}")
                self.root.after(0, lambda: self._update_auth_status(False, f"Failed to download authentication data: {result}"))
                return
            
            # Parse keys data
            try:
                print("Parsing keys data...")
                keys_data = json.loads(result)
                print(f"Keys data parsed successfully: {len(keys_data.get('keys', []))} keys found")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                self.root.after(0, lambda: self._update_auth_status(False, "Invalid authentication data format"))
                return
            
            # Verify license key
            print(f"Verifying license key: {license_key}")
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
            
            if not valid_key:
                print(f"No valid key found matching: {license_key}")
                self.root.after(0, lambda: self._update_auth_status(False, "Invalid license key"))
                return
            
            # Check HWID (hardware ID)
            # If HWID is empty, this is first use
            # If HWID is set but doesn't match current machine, reject
            current_hwid = str(uuid.getnode())  # MAC address as HWID
            
            if key_info and "hwid" in key_info:
                stored_hwid = key_info.get("hwid", "")
                if stored_hwid and stored_hwid != current_hwid:
                    self.root.after(0, lambda: self._update_auth_status(False, "This license key is bound to another machine"))
                    return
            
            # Authentication successful
            # Store user info
            self.user_info = {
                "key": license_key,
                "uses_remaining": key_info.get("uses_remaining", 0) if key_info else 0,
                "hwid": current_hwid
            }
            
            # Update the key in GitHub
            # 1. Decrement the uses remaining
            # 2. Set the HWID if not already set
            # First get the file SHA (required for GitHub API update)
            sha = self.get_sha_of_file()
            if sha:
                # Update the key data
                keys_data["keys"][key_index]["uses_remaining"] -= 1
                if not keys_data["keys"][key_index].get("hwid"):
                    keys_data["keys"][key_index]["hwid"] = current_hwid
                
                # Update the file on GitHub
                self.update_keys_on_github(keys_data, sha)
            
            # Return successful authentication
            uses_remaining = self.user_info.get('uses_remaining', 0) - 1  # Already decremented
            
            self.root.after(0, lambda: self._update_auth_status(True, f"Authentication successful! Uses remaining: {uses_remaining}"))
            
        except Exception as e:
            self.root.after(0, lambda: self._update_auth_status(False, f"Authentication error: {str(e)}"))
    
    def _update_auth_status(self, success, message):
        """Update authentication status on the main thread"""
        if success:
            self.login_status_label.config(fg=COLORS["success"])
            self.login_status_var.set(message)
            self.authenticated = True
            
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
        
        # Create the main application with authenticated user info
        app = RuneSlayerTool(self.root, self.user_info)
    
    def download_file_from_github(self, file_path):
        """Download a file from GitHub"""
        # Construct GitHub API URL
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{file_path}"
        
        # Setup headers
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        try:
            # Make the request
            response = requests.get(url, headers=headers)
            
            # Check for successful response
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                
                # Make sure the content is of type "file"
                if "type" not in data or data["type"] != "file":
                    return False, "The specified path is not a file"
                
                # Decode the Base64 encoded content
                content = base64.b64decode(data["content"])
                
                # Return content as string
                return True, content.decode('utf-8')
            else:
                # Handle error response
                error_message = f"Failed to download file. Status code: {response.status_code}"
                try:
                    error_message += f", Message: {response.json().get('message', '')}"
                except:
                    pass
                return False, error_message
        
        except Exception as e:
            # Handle exceptions
            return False, f"An error occurred: {str(e)}"


def main(user_info=None):
    """Main entry point"""
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
        
        # If user info is provided, skip authentication
        if user_info is not None:
            # Create application
            app = RuneSlayerTool(root, user_info)
        else:
            # Create authentication app
            auth_app = AuthenticationApp(root)
        
        # Start main loop
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_tb(e.__traceback__)

if __name__ == "__main__":
    main()
