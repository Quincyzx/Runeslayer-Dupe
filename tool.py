#!/usr/bin/env python3
"""
Tact Tool - Main Application
Enhanced UI version with improved user experience
"""
import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import datetime
import tempfile
import atexit
import threading
from auth_utils import verify_license, update_usage, get_system_id
from ui_helpers import create_tooltip, create_button, create_input, HoverButton, RoundedFrame

# Configuration
APP_TITLE = "Tact Tool"
VERSION = "1.1"

# Modern dark theme colors - Enhanced from original
COLORS = {
    "background": "#121212",          # Darker background
    "secondary_bg": "#1e1e1e",        # Slightly lighter background
    "tertiary_bg": "#2a2a2a",         # Tertiary background for contrast
    "accent": "#00b4ff",              # Bright cyan accent
    "accent_hover": "#0095d9",        # Hover state for accent color
    "accent_disabled": "#005e8a",     # Disabled state for accent
    "text": "#ffffff",                # Primary text color
    "text_secondary": "#858585",      # Secondary text color
    "text_disabled": "#555555",       # Disabled text
    "success": "#2ecc71",             # Success indicator
    "warning": "#f1c40f",             # Warning indicator
    "danger": "#e74c3c",              # Danger/error indicator
    "danger_hover": "#c0392b",        # Hover state for danger
    "border": "#2a2a2a",              # Border color
    "input_bg": "#1a1a1a",            # Input field background
    "tab_active": "#00b4ff",          # Active tab
    "tab_inactive": "#1a1a1a",        # Inactive tab
    "tab_hover": "#252525",           # Tab hover state
    "card_bg": "#1a1a1a",             # Card background
    "divider": "#333333"              # Divider line color
}

# UI Constants
FONT_FAMILY = "Segoe UI" if sys.platform == "win32" else "Arial"
BUTTON_FONT = (FONT_FAMILY, 11, "bold")
HEADER_FONT = (FONT_FAMILY, 24, "bold")
TITLE_FONT = (FONT_FAMILY, 32, "bold")
LABEL_FONT = (FONT_FAMILY, 11)
INPUT_FONT = (FONT_FAMILY, 12)
STATUS_FONT = (FONT_FAMILY, 10)
INFO_FONT = (FONT_FAMILY, 12)
INFO_VALUE_FONT = (FONT_FAMILY, 12, "bold")
TAB_FONT = (FONT_FAMILY, 11)

# Icons (using SVG for vector graphics)
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.svg")

class TactTool:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_TITLE} v{VERSION}")
        self.root.geometry("900x600")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["background"])

        # Center window
        self.center_window()

        # Variables
        self.script_dir = os.environ.get("TACT_SCRIPT_DIR", os.path.dirname(__file__))
        self.keys_file = os.path.join(self.script_dir, "keys.json")
        self.license_key = None
        self.user_info = None
        
        # Check for first run
        self.first_run = not os.path.exists(self.keys_file)

        # Configure ttk styles
        self.setup_styles()

        # Set up authentication UI
        self.setup_auth_ui()

        # Register cleanup
        if os.environ.get("TACT_CLEANUP_ON_EXIT") == "1":
            atexit.register(self.cleanup)
            
        # Add window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_styles(self):
        """Set up custom ttk styles"""
        style = ttk.Style()

        # Configure notebook (tab container)
        style.configure(
            "Custom.TNotebook",
            background=COLORS["background"],
            borderwidth=0,
            padding=0
        )

        # Configure notebook tabs
        style.configure(
            "Custom.TNotebook.Tab",
            padding=[20, 12],
            background=COLORS["tab_inactive"],
            foreground=COLORS["text"],
            font=TAB_FONT
        )

        style.map(
            "Custom.TNotebook.Tab",
            background=[
                ("selected", COLORS["tab_active"]),
                ("active", COLORS["tab_hover"])
            ],
            foreground=[
                ("selected", COLORS["text"]),
                ("active", COLORS["text"])
            ]
        )

        # Configure frames
        style.configure(
            "Custom.TFrame",
            background=COLORS["background"]
        )
        
        # Configure separator
        style.configure(
            "Custom.TSeparator",
            background=COLORS["divider"]
        )

    def setup_auth_ui(self):
        """Set up the authentication UI"""
        # Main container with a gradient background effect
        self.auth_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.auth_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=450)

        # App logo (if available)
        try:
            if os.path.exists(LOGO_PATH):
                logo_img = tk.PhotoImage(file=LOGO_PATH)
                logo_label = tk.Label(
                    self.auth_frame, 
                    image=logo_img, 
                    bg=COLORS["background"]
                )
                logo_label.image = logo_img  # Keep a reference to prevent garbage collection
                logo_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"Logo load error: {e}")
            pass  # Continue without logo if it fails to load

        # Title
        title_label = tk.Label(
            self.auth_frame,
            text="Tact Tool",
            font=TITLE_FONT,
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack(pady=(0, 30))

        # Authentication card with elevated effect
        auth_card = RoundedFrame(self.auth_frame, bg=COLORS["secondary_bg"], radius=10)
        auth_card.pack(fill=tk.X, padx=20, pady=10)
        
        # Padding inside card
        inner_frame = tk.Frame(auth_card, bg=COLORS["secondary_bg"], padx=25, pady=25)
        inner_frame.pack(fill=tk.X)

        # License key label
        key_label = tk.Label(
            inner_frame,
            text="License Key",
            font=LABEL_FONT,
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        key_label.pack(anchor=tk.W, pady=(0, 5))

        # License key input with modern styling
        key_container = tk.Frame(inner_frame, bg=COLORS["secondary_bg"])
        key_container.pack(fill=tk.X, pady=(0, 20))
        
        self.key_entry = create_input(
            key_container,
            placeholder="Enter your license key",
            font=INPUT_FONT,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            bd=0,
            padx=15,
            pady=10
        )

        # Login button with hover effect
        self.login_button = HoverButton(
            inner_frame,
            text="ACTIVATE LICENSE",
            font=BUTTON_FONT,
            bg=COLORS["accent"],
            fg=COLORS["text"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text"],
            padx=40,
            pady=12,
            command=self.login
        )
        self.login_button.pack(fill=tk.X, pady=(10, 5))
        
        # Create tooltip for the login button
        create_tooltip(self.login_button, "Verify your license key and access the tool")

        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Enter your license key to continue")

        self.status_label = tk.Label(
            inner_frame,
            textvariable=self.status_var,
            font=STATUS_FONT,
            bg=COLORS["secondary_bg"],
            fg=COLORS["text_secondary"],
            wraplength=390,
            justify=tk.CENTER
        )
        self.status_label.pack(pady=(10, 0))
        
        # Footer with version info
        footer_frame = tk.Frame(self.auth_frame, bg=COLORS["background"])
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        version_label = tk.Label(
            footer_frame,
            text=f"Version {VERSION}",
            font=(FONT_FAMILY, 9),
            bg=COLORS["background"],
            fg=COLORS["text_secondary"]
        )
        version_label.pack(side=tk.RIGHT, padx=20)

    def login(self):
        """Handle login attempt with visual feedback"""
        # Change button appearance to show processing
        self.login_button.config(
            text="VERIFYING...", 
            state=tk.DISABLED,
            bg=COLORS["accent_disabled"]
        )
        self.status_var.set("Verifying your license key...")
        self.root.update()
        
        # Get the license key
        key = self.key_entry.get().strip()
        if not key:
            self.status_var.set("Please enter a license key")
            self.login_button.config(
                text="ACTIVATE LICENSE",
                state=tk.NORMAL,
                bg=COLORS["accent"]
            )
            return
        
        # Use threading to prevent UI freezing
        threading.Thread(target=self._verify_license, args=(key,), daemon=True).start()

    def _verify_license(self, key):
        """Verify license in background thread"""
        try:
            # Verify license
            success, user_data, message = verify_license(key, self.keys_file)
            
            # Use after() to safely update UI from thread
            if success:
                self.license_key = key
                self.user_info = user_data
                
                # Update status message
                self.root.after(0, lambda: self.status_var.set("License verified successfully! Loading application..."))
                
                # Update usage count in background
                try:
                    update_success, update_message = update_usage(key, self.keys_file)
                    if not update_success:
                        print(f"Warning: {update_message}")
                except Exception as e:
                    print(f"Usage update error: {e}")
                
                # Switch to main UI after a short delay for better visual feedback
                self.root.after(1000, self.setup_main_ui)
            else:
                # Show error message
                self.root.after(0, lambda: self.status_label.config(fg=COLORS["danger"]))
                self.root.after(0, lambda: self.status_var.set(f"Authentication failed: {message}"))
                self.root.after(0, lambda: self.login_button.config(
                    text="RETRY",
                    state=tk.NORMAL,
                    bg=COLORS["accent"]
                ))
                
        except Exception as e:
            error_msg = f"Authentication error: {str(e)}"
            self.root.after(0, lambda: self.status_label.config(fg=COLORS["danger"]))
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: self.login_button.config(
                text="RETRY",
                state=tk.NORMAL,
                bg=COLORS["accent"]
            ))

    def setup_main_ui(self):
        """Set up the main UI after authentication"""
        # Remove authentication UI
        self.auth_frame.destroy()
        
        # Create main app container
        self.app_container = tk.Frame(self.root, bg=COLORS["background"])
        self.app_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header()
        
        # Create main content area with tabs
        self.content_frame = tk.Frame(self.app_container, bg=COLORS["background"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.content_frame, style="Custom.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create Dashboard tab
        self.dashboard_tab = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.setup_dashboard_tab()
        
        # Create Profile tab
        self.profile_tab = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(self.profile_tab, text="Profile")
        self.setup_profile_tab()

        # Create Settings tab
        self.settings_tab = ttk.Frame(self.notebook, style="Custom.TFrame")
        self.notebook.add(self.settings_tab, text="Settings")
        self.setup_settings_tab()
        
        # Create footer with exit button
        self.create_footer()
        
    def create_header(self):
        """Create the application header"""
        header_frame = tk.Frame(self.app_container, bg=COLORS["background"], height=70)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)  # Maintain fixed height
        
        # App title
        title_label = tk.Label(
            header_frame,
            text=APP_TITLE,
            font=HEADER_FONT,
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack(side=tk.LEFT)
        
        # User info section
        user_frame = tk.Frame(header_frame, bg=COLORS["background"])
        user_frame.pack(side=tk.RIGHT)
        
        # Username or license info
        user_name = self.user_info.get('name', 'User')
        user_label = tk.Label(
            user_frame,
            text=f"Welcome, {user_name}",
            font=(FONT_FAMILY, 12),
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        user_label.pack(side=tk.RIGHT)
        
        # Divider line
        divider = ttk.Separator(self.app_container, orient='horizontal', style="Custom.TSeparator")
        divider.pack(fill=tk.X, padx=20, pady=(0, 10))

    def create_footer(self):
        """Create application footer"""
        footer_frame = tk.Frame(self.app_container, bg=COLORS["background"], height=60)
        footer_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # Version info
        version_label = tk.Label(
            footer_frame,
            text=f"Version {VERSION}",
            font=(FONT_FAMILY, 9),
            bg=COLORS["background"],
            fg=COLORS["text_secondary"]
        )
        version_label.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_button = HoverButton(
            footer_frame,
            text="EXIT",
            font=BUTTON_FONT,
            bg=COLORS["danger"],
            fg=COLORS["text"],
            activebackground=COLORS["danger_hover"],
            activeforeground=COLORS["text"],
            padx=30,
            pady=10,
            command=self.exit_application
        )
        exit_button.pack(side=tk.RIGHT)
        
    def setup_dashboard_tab(self):
        """Set up the dashboard tab content"""
        dashboard_frame = tk.Frame(self.dashboard_tab, bg=COLORS["background"])
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Title
        title_label = tk.Label(
            dashboard_frame,
            text="Dashboard",
            font=HEADER_FONT,
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Main dashboard content
        content_frame = RoundedFrame(dashboard_frame, bg=COLORS["secondary_bg"], radius=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inner padding
        inner_dash = tk.Frame(content_frame, bg=COLORS["secondary_bg"], padx=30, pady=30)
        inner_dash.pack(fill=tk.BOTH, expand=True)
        
        # Welcome message
        welcome_text = tk.Label(
            inner_dash,
            text=f"Welcome to Tact Tool v{VERSION}",
            font=(FONT_FAMILY, 18, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        welcome_text.pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        description = tk.Label(
            inner_dash,
            text="Your premium tool with license protection and HWID verification.",
            font=(FONT_FAMILY, 12),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text_secondary"],
            wraplength=800,
            justify=tk.LEFT
        )
        description.pack(anchor=tk.W, pady=(0, 30))
        
        # Stats cards container
        stats_frame = tk.Frame(inner_dash, bg=COLORS["secondary_bg"])
        stats_frame.pack(fill=tk.X, pady=(0, 30))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        
        # Stats cards
        self.create_stat_card(stats_frame, "Remaining Uses", 
                              str(max(0, self.user_info.get('uses_remaining', 0) - 1)), 
                              COLORS["accent"], 0, 0)
        
        self.create_stat_card(stats_frame, "License Type", 
                              self.user_info.get('type', 'Standard'), 
                              COLORS["success"], 0, 1)
        
        self.create_stat_card(stats_frame, "Status", 
                              "Active", 
                              COLORS["success"], 0, 2)
        
        # Tool functionality section
        tools_label = tk.Label(
            inner_dash,
            text="Tool Functions",
            font=(FONT_FAMILY, 16, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        tools_label.pack(anchor=tk.W, pady=(20, 15))
        
        # Tool buttons container
        tool_buttons_frame = tk.Frame(inner_dash, bg=COLORS["secondary_bg"])
        tool_buttons_frame.pack(fill=tk.X)
        
        # Tool buttons
        tool_btn1 = HoverButton(
            tool_buttons_frame,
            text="Function 1",
            font=BUTTON_FONT,
            bg=COLORS["tertiary_bg"],
            fg=COLORS["text"],
            activebackground=COLORS["tab_hover"],
            activeforeground=COLORS["text"],
            padx=20,
            pady=15,
            command=lambda: self.run_tool_function("function1")
        )
        tool_btn1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        tool_btn2 = HoverButton(
            tool_buttons_frame,
            text="Function 2",
            font=BUTTON_FONT,
            bg=COLORS["tertiary_bg"],
            fg=COLORS["text"],
            activebackground=COLORS["tab_hover"],
            activeforeground=COLORS["text"],
            padx=20,
            pady=15,
            command=lambda: self.run_tool_function("function2")
        )
        tool_btn2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        tool_btn3 = HoverButton(
            tool_buttons_frame,
            text="Function 3",
            font=BUTTON_FONT,
            bg=COLORS["tertiary_bg"],
            fg=COLORS["text"],
            activebackground=COLORS["tab_hover"],
            activeforeground=COLORS["text"],
            padx=20,
            pady=15,
            command=lambda: self.run_tool_function("function3")
        )
        tool_btn3.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Configure grid for equal width columns
        tool_buttons_frame.grid_columnconfigure(0, weight=1)
        tool_buttons_frame.grid_columnconfigure(1, weight=1)
        tool_buttons_frame.grid_columnconfigure(2, weight=1)
        
        # Log section
        log_label = tk.Label(
            inner_dash,
            text="Activity Log",
            font=(FONT_FAMILY, 16, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        log_label.pack(anchor=tk.W, pady=(30, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            inner_dash,
            font=(FONT_FAMILY, 10),
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            height=8,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Session started\n")
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] License verified successfully\n")
        self.log_text.config(state=tk.DISABLED)  # Make read-only
        
    def create_stat_card(self, parent, title, value, color, row, col):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=COLORS["tertiary_bg"], padx=20, pady=15)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Title
        title_label = tk.Label(
            card,
            text=title,
            font=(FONT_FAMILY, 11),
            bg=COLORS["tertiary_bg"],
            fg=COLORS["text_secondary"]
        )
        title_label.pack(anchor=tk.W)
        
        # Value with color indicator
        value_frame = tk.Frame(card, bg=COLORS["tertiary_bg"])
        value_frame.pack(fill=tk.X, pady=(5, 0))
        
        color_indicator = tk.Frame(value_frame, bg=color, width=3)
        color_indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        value_label = tk.Label(
            value_frame,
            text=value,
            font=(FONT_FAMILY, 16, "bold"),
            bg=COLORS["tertiary_bg"],
            fg=COLORS["text"]
        )
        value_label.pack(side=tk.LEFT)
        
    def run_tool_function(self, function_name):
        """Run a tool function and update the log"""
        try:
            # Enable editing
            self.log_text.config(state=tk.NORMAL)
            
            # Add log entry
            self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Running {function_name}...\n")
            
            # This is where you would implement the actual tool function
            time.sleep(0.5)  # Simulate processing
            
            # Add success message
            self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {function_name} completed successfully\n")
            
            # Scroll to the end
            self.log_text.see(tk.END)
            
            # Make read-only again
            self.log_text.config(state=tk.DISABLED)
            
        except Exception as e:
            # Log error
            self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Error in {function_name}: {str(e)}\n")
            self.log_text.config(state=tk.DISABLED)
            messagebox.showerror("Function Error", f"Error in {function_name}: {str(e)}")

    def setup_profile_tab(self):
        """Set up the profile tab content"""
        profile_frame = tk.Frame(self.profile_tab, bg=COLORS["background"])
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Title
        title_label = tk.Label(
            profile_frame,
            text="User Profile",
            font=HEADER_FONT,
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack(anchor=tk.W, pady=(0, 20))

        # Profile container
        profile_container = RoundedFrame(profile_frame, bg=COLORS["secondary_bg"], radius=10)
        profile_container.pack(fill=tk.BOTH, expand=True)
        
        # Inner padding
        inner_profile = tk.Frame(profile_container, bg=COLORS["secondary_bg"], padx=30, pady=30)
        inner_profile.pack(fill=tk.BOTH, expand=True)
        
        # License info section
        license_frame = tk.Frame(inner_profile, bg=COLORS["secondary_bg"])
        license_frame.pack(fill=tk.X, pady=(0, 20))
        
        license_title = tk.Label(
            license_frame,
            text="License Information",
            font=(FONT_FAMILY, 16, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        license_title.pack(anchor=tk.W, pady=(0, 15))
        
        # License details in a card
        license_card = tk.Frame(license_frame, bg=COLORS["tertiary_bg"], padx=25, pady=20)
        license_card.pack(fill=tk.X)
        
        # License Key
        self.create_info_row(license_card, "License Key", self.license_key, 0)
        
        # Uses info
        uses_remaining = max(0, self.user_info.get('uses_remaining', 0) - 1)
        self.create_info_row(license_card, "Uses Remaining", str(uses_remaining), 1)
        
        # License Type
        license_type = self.user_info.get('type', 'Standard')
        self.create_info_row(license_card, "License Type", license_type, 2)
        
        # User Since
        user_since = self.user_info.get('created_at', 'N/A')
        self.create_info_row(license_card, "User Since", user_since, 3)
        
        # Expiration
        expiration = self.user_info.get('expires_at', 'N/A')
        self.create_info_row(license_card, "Expiration", expiration, 4)
        
        # Hardware information section
        hardware_frame = tk.Frame(inner_profile, bg=COLORS["secondary_bg"])
        hardware_frame.pack(fill=tk.X, pady=(20, 0))
        
        hardware_title = tk.Label(
            hardware_frame,
            text="Hardware Information",
            font=(FONT_FAMILY, 16, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        hardware_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Hardware details in a card
        hardware_card = tk.Frame(hardware_frame, bg=COLORS["tertiary_bg"], padx=25, pady=20)
        hardware_card.pack(fill=tk.X)
        
        # HWID
        hwid = self.user_info.get('hwid', 'Not registered')
        self.create_info_row(hardware_card, "Hardware ID", hwid[:20] + "...", 0)
        
        # System info
        import platform
        system_info = f"{platform.system()} {platform.release()}"
        self.create_info_row(hardware_card, "Operating System", system_info, 1)
        
        # Processor
        processor = platform.processor() or "Unknown"
        self.create_info_row(hardware_card, "Processor", processor, 2)
        
        # Machine
        machine = platform.machine()
        self.create_info_row(hardware_card, "Architecture", machine, 3)

    def create_info_row(self, parent, label, value, row):
        """Create a row of information in the profile tab"""
        # Label
        tk.Label(
            parent,
            text=label,
            font=INFO_FONT,
            bg=COLORS["tertiary_bg"],
            fg=COLORS["text_secondary"]
        ).grid(row=row, column=0, padx=5, pady=10, sticky=tk.W)

        # Value
        tk.Label(
            parent,
            text=value,
            font=INFO_VALUE_FONT,
            bg=COLORS["tertiary_bg"],
            fg=COLORS["text"]
        ).grid(row=row, column=1, padx=20, pady=10, sticky=tk.W)
        
    def setup_settings_tab(self):
        """Set up the settings tab content"""
        settings_frame = tk.Frame(self.settings_tab, bg=COLORS["background"])
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Title
        title_label = tk.Label(
            settings_frame,
            text="Settings",
            font=HEADER_FONT,
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Settings container
        settings_container = RoundedFrame(settings_frame, bg=COLORS["secondary_bg"], radius=10)
        settings_container.pack(fill=tk.BOTH, expand=True)
        
        # Inner padding
        inner_settings = tk.Frame(settings_container, bg=COLORS["secondary_bg"], padx=30, pady=30)
        inner_settings.pack(fill=tk.BOTH, expand=True)
        
        # Application Settings section
        app_settings_title = tk.Label(
            inner_settings,
            text="Application Settings",
            font=(FONT_FAMILY, 16, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        app_settings_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Settings options
        settings_options = tk.Frame(inner_settings, bg=COLORS["secondary_bg"])
        settings_options.pack(fill=tk.X, pady=(0, 30))
        
        # Auto-start option
        autostart_var = tk.BooleanVar(value=False)
        autostart_check = tk.Checkbutton(
            settings_options,
            text="Start automatically with system",
            variable=autostart_var,
            font=INFO_FONT,
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["background"],
            activebackground=COLORS["secondary_bg"],
            activeforeground=COLORS["text"]
        )
        autostart_check.pack(anchor=tk.W, pady=5)
        
        # Remember license option
        remember_var = tk.BooleanVar(value=True)
        remember_check = tk.Checkbutton(
            settings_options,
            text="Remember license key",
            variable=remember_var,
            font=INFO_FONT,
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["background"],
            activebackground=COLORS["secondary_bg"],
            activeforeground=COLORS["text"]
        )
        remember_check.pack(anchor=tk.W, pady=5)
        
        # Check for updates option
        updates_var = tk.BooleanVar(value=True)
        updates_check = tk.Checkbutton(
            settings_options,
            text="Check for updates on startup",
            variable=updates_var,
            font=INFO_FONT,
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["background"],
            activebackground=COLORS["secondary_bg"],
            activeforeground=COLORS["text"]
        )
        updates_check.pack(anchor=tk.W, pady=5)
        
        # Settings actions section
        actions_frame = tk.Frame(inner_settings, bg=COLORS["secondary_bg"])
        actions_frame.pack(fill=tk.X, pady=(20, 0))
        
        save_button = HoverButton(
            actions_frame,
            text="SAVE SETTINGS",
            font=BUTTON_FONT,
            bg=COLORS["accent"],
            fg=COLORS["text"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text"],
            padx=20,
            pady=12,
            command=lambda: self.save_settings(autostart_var.get(), remember_var.get(), updates_var.get())
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        reset_button = HoverButton(
            actions_frame,
            text="RESET",
            font=BUTTON_FONT,
            bg=COLORS["tertiary_bg"],
            fg=COLORS["text"],
            activebackground=COLORS["tab_hover"],
            activeforeground=COLORS["text"],
            padx=20,
            pady=12,
            command=self.reset_settings
        )
        reset_button.pack(side=tk.LEFT)
        
        # About section
        about_title = tk.Label(
            inner_settings,
            text="About",
            font=(FONT_FAMILY, 16, "bold"),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"]
        )
        about_title.pack(anchor=tk.W, pady=(40, 15))
        
        about_text = tk.Label(
            inner_settings,
            text=f"Tact Tool v{VERSION}\n\nA license-protected application with HWID verification and usage tracking.",
            font=INFO_FONT,
            bg=COLORS["secondary_bg"],
            fg=COLORS["text"],
            justify=tk.LEFT
        )
        about_text.pack(anchor=tk.W)
        
    def save_settings(self, autostart, remember, updates):
        """Save user settings"""
        try:
            # This would typically save to a configuration file
            settings = {
                "autostart": autostart,
                "remember_license": remember,
                "check_updates": updates
            }
            
            # Show success message
            messagebox.showinfo("Settings", "Settings saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # This would reset checkboxes and other options
            messagebox.showinfo("Settings", "Settings have been reset to defaults")

    def exit_application(self):
        """Exit the application with confirmation"""
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
