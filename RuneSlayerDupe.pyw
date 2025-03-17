import sys
import os
import json
import string
import random
import requests
import uuid
import hashlib
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget
from PySide6.QtCore import Qt

# Dictionary to store username and generated key
generated_keys = {}

# Function to get the hardware ID of the current machine
def get_hardware_id():
    # Create a unique hardware ID based on machine-specific identifiers
    # This combines multiple system identifiers for a more robust HWID
    try:
        # Get system UUID
        system_uuid = str(uuid.uuid1()).encode()
        
        # Get MAC address (first available)
        mac = uuid.getnode()
        mac_bytes = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2)).encode()
        
        # Get computer name
        computer_name = os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', '')).encode()
        
        # Combine and hash to create a stable HWID
        combined = system_uuid + mac_bytes + computer_name
        hwid = hashlib.sha256(combined).hexdigest()
        return hwid
    except Exception as e:
        print(f"Error getting HWID: {e}")
        # Fallback to a simple UUID-based identifier if there's an error
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

# Function to generate a unique key (based on username and a random component)
def generate_key(username):
    # Create a key that combines username hash with randomness
    # This ensures keys are unique even for the same username
    username_hash = hashlib.md5(username.encode()).hexdigest()[:6]
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{username_hash}-{random_part}"

# Function to check if key exists in the keys.json from GitHub
def validate_key_with_github(username, key, hwid):
    # Load the keys.json file
    try:
        if os.path.exists("keys.json"):
            with open("keys.json", "r") as f:
                keys_data = json.load(f)
                
            # Check if username exists and key matches
            if username in keys_data:
                stored_key = keys_data[username].get("key", "")
                stored_hwid = keys_data[username].get("hwid", "0")
                
                # Validate key
                if stored_key != key:
                    return False, "Invalid key for this username"
                
                # Check HWID
                if stored_hwid == "0":
                    # First-time use, update HWID
                    keys_data[username]["hwid"] = hwid
                    with open("keys.json", "w") as f:
                        json.dump(keys_data, f, indent=4)
                    return True, "First-time use, HWID registered"
                elif stored_hwid != hwid:
                    return False, "HWID mismatch - this key is registered to another device"
                    
                return True, "Key validated successfully"
            else:
                return False, "Username not found"
        else:
            return False, "Keys file not found"
    except Exception as e:
        print(f"Error validating key: {e}")
        return False, f"Error validating key: {str(e)}"

# Function to send logs to Discord webhook with an embed
def send_to_discord_with_embed(username, key, action, hwid):
    webhook_url = "https://discord.com/api/webhooks/1350911020146626784/F6QkaNdxIQCccpWtkBS6yrQykgsIG3j1B_ltAGARhJkGLObpiQCCwMSAtUDaLtSmldKd"
    
    embed_data = {
        "embeds": [
            {
                "title": f"Action Logged - {action}",
                "description": f"**Username**: {username}\n**Key Used**: {key}\n**Action**: {action}\n**HWID**: {hwid}",
                "color": 0xCB6CE6,  # Purple color
                "fields": [
                    {
                        "name": "Username",
                        "value": username,
                        "inline": True
                    },
                    {
                        "name": "Key",
                        "value": key,
                        "inline": True
                    },
                    {
                        "name": "Action",
                        "value": action,
                        "inline": True
                    },
                    {
                        "name": "HWID",
                        "value": hwid,
                        "inline": False
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=embed_data)
        response.raise_for_status()  # Raise an error for bad status codes
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")
        return False  # Return false if the webhook fails

# Function to block Roblox (simulate disconnect)
def block_roblox(username, key):
    os.system("netsh advfirewall firewall add rule name='BlockRoblox' dir=out action=block remoteip=128.116.0.0/16")
    print(f"Roblox connection blocked for {username} using key {key}!")  # Simulate the Roblox blocking
    send_to_discord_with_embed(username, key, "Start Dupe", get_hardware_id())

# Function to unblock Roblox (simulate reconnect)
def unblock_roblox(username, key):
    os.system("netsh advfirewall firewall delete rule name='BlockRoblox'")
    print(f"Roblox connection restored for {username} using key {key}!")  # Simulate the Roblox reconnect
    send_to_discord_with_embed(username, key, "End Dupe", get_hardware_id())

# Load config from launcher
def load_config():
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as config_file:
                return json.load(config_file)
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

class TactDupeApp(QWidget):
    def __init__(self, username=""):
        super().__init__()

        # Window settings
        self.setWindowTitle("Tact RuneSlayer Dupe")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1a1a1a; color: #ffffff; font-family: Arial;")
        
        # Store username from command line or config
        self.stored_username = username
        
        # Load config from launcher if available
        self.config = load_config()
        
        # Store hardware ID
        self.hwid = get_hardware_id()
        print(f"Hardware ID: {self.hwid}")
        
        # Initialize UI
        self.init_ui()
        
        # Auto-fill username if provided
        if self.stored_username:
            self.username_input.setText(self.stored_username)
            self.keys_left_label.setText(f"Keys Left: {self.config.get('keys_left', 'Unknown')}")

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget()

        # Page 1 - Username Entry
        self.page1 = QWidget()
        self.page1_layout = QVBoxLayout()

        title_label = QLabel("Tact RuneSlayer Dupe", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; color: #CB6CE6; font-weight: bold;")
        self.page1_layout.addWidget(title_label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter your Username")
        self.username_input.setStyleSheet("background-color: #333333; border: 1px solid #CB6CE6; padding: 10px;")
        self.page1_layout.addWidget(self.username_input)
        
        # Add keys left label
        self.keys_left_label = QLabel("Keys Left: Unknown", self)
        self.keys_left_label.setAlignment(Qt.AlignCenter)
        self.keys_left_label.setStyleSheet("font-size: 14px; color: #CB6CE6;")
        self.page1_layout.addWidget(self.keys_left_label)

        # Add HWID label
        hwid_label = QLabel(f"HWID: {self.hwid[:8]}...{self.hwid[-8:]}", self)
        hwid_label.setAlignment(Qt.AlignCenter)
        hwid_label.setStyleSheet("font-size: 12px; color: #888888;")
        self.page1_layout.addWidget(hwid_label)

        generate_button = QPushButton("Generate Key", self)
        generate_button.setStyleSheet("background-color: #CB6CE6; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        generate_button.clicked.connect(self.generate_key)
        self.page1_layout.addWidget(generate_button)

        self.page1.setLayout(self.page1_layout)

        # Page 2 - Key Entry
        self.page2 = QWidget()
        self.page2_layout = QVBoxLayout()

        self.key_label = QLabel("Enter the key that was sent to you", self)
        self.key_label.setAlignment(Qt.AlignCenter)
        self.key_label.setStyleSheet("font-size: 16px; color: #CB6CE6; font-weight: bold;")
        self.page2_layout.addWidget(self.key_label)

        self.key_input = QLineEdit(self)
        self.key_input.setPlaceholderText("Enter your Key")
        self.key_input.setStyleSheet("background-color: #333333; border: 1px solid #CB6CE6; padding: 10px;")
        self.page2_layout.addWidget(self.key_input)

        validate_button = QPushButton("Validate Key", self)
        validate_button.setStyleSheet("background-color: #CB6CE6; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        validate_button.clicked.connect(self.validate_key)
        self.page2_layout.addWidget(validate_button)

        self.page2.setLayout(self.page2_layout)

        # Page 3 - Dupe and End Dupe
        self.page3 = QWidget()
        self.page3_layout = QVBoxLayout()

        self.dupe_label = QLabel("Tact RuneSlayer Dupe", self)
        self.dupe_label.setAlignment(Qt.AlignCenter)
        self.dupe_label.setStyleSheet("font-size: 20px; color: #CB6CE6; font-weight: bold;")
        self.page3_layout.addWidget(self.dupe_label)

        self.dupe_button = QPushButton("Start Dupe", self)
        self.dupe_button.setStyleSheet("background-color: #CB6CE6; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        self.dupe_button.clicked.connect(self.block_roblox)
        self.page3_layout.addWidget(self.dupe_button)

        self.end_dupe_button = QPushButton("End Dupe", self)
        self.end_dupe_button.setStyleSheet("background-color: #e74c3c; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        self.end_dupe_button.clicked.connect(self.unblock_roblox)
        self.page3_layout.addWidget(self.end_dupe_button)

        self.page3.setLayout(self.page3_layout)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)
        self.stacked_widget.addWidget(self.page3)

        # Set initial page
        self.stacked_widget.setCurrentIndex(0)

        # Set layout
        self.layout.addWidget(self.stacked_widget)
        self.setLayout(self.layout)

    def generate_key(self):
        username = self.username_input.text()

        if not username:
            QMessageBox.warning(self, "Input Error", "Please enter a username before proceeding.")
            return
          
        # Generate a unique key
        key = generate_key(username)
        generated_keys[username] = key  # Store the generated key with the username
        print(f"Generated key for {username}: {key}")
        
        # Try to update keys.json with the new key
        try:
            keys_data = {}
            if os.path.exists("keys.json"):
                with open("keys.json", "r") as f:
                    keys_data = json.load(f)
            
            if username in keys_data:
                keys_data[username]["key"] = key
            else:
                keys_data[username] = {"key": key, "hwid": "0", "keys_left": 5}
                
            with open("keys.json", "w") as f:
                json.dump(keys_data, f, indent=4)
                
            print(f"Updated keys.json with new key for {username}")
        except Exception as e:
            print(f"Error updating keys.json: {e}")

        # Send key and username to Discord with embed
        if send_to_discord_with_embed(username, key, "Generated Key", self.hwid):
            # Move to the next page if the webhook is successful
            self.stacked_widget.setCurrentIndex(1)  # Switch to the next page for key entry
            QMessageBox.information(self, "Key Generated", f"Your key is: {key}\n\nThis key has been sent to the admin for verification.")
        else:
            QMessageBox.warning(self, "Error", "Failed to send data to Discord. Please check your connection.")

    def validate_key(self):
        entered_key = self.key_input.text()
        username = self.username_input.text()

        if not entered_key:
            QMessageBox.warning(self, "Validation Error", "Please enter the key.")
            return

        # Validate the key and check HWID
        valid, message = validate_key_with_github(username, entered_key, self.hwid)
        
        if valid:
            QMessageBox.information(self, "Success", message)
            send_to_discord_with_embed(username, entered_key, "Key Validated", self.hwid)
            self.stacked_widget.setCurrentIndex(2)  # Switch to the dupe functionality page

    def block_roblox(self):
        username = self.username_input.text()
        key = generated_keys.get(username)
        
        if not username or not key:
            QMessageBox.warning(self, "Error", "Please generate a key first.")
            return
        
        # Block Roblox connection
        block_roblox(username, key)
        QMessageBox.information(self, "Dupe Started", "Roblox has been blocked. Dupe process started.")

    def unblock_roblox(self):
        username = self.username_input.text()
        key = generated_keys.get(username)
        
        if not username or not key:
            QMessageBox.warning(self, "Error", "Please generate a key first.")
            return
        
        # Unblock Roblox connection
        unblock_roblox(username, key)
        QMessageBox.information(self, "Dupe Ended", "Roblox connection restored. Dupe process ended.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TactDupeApp()  # Optionally pass a username here if you have one
    window.show()
    sys.exit(app.exec())
