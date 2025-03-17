import os
import sys
import json
import hashlib
import random
import string
import requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget
from PySide6.QtCore import Qt

# Constants
KEYS_FILE = "keys.json"
WEBHOOK_URL = "https://discord.com/api/webhooks/1350911020146626784/F6QkaNdxIQCccpWtkBS6yrQykgsIG3j1B_ltAGARhJkGLObpiQCCwMSAtUDaLtSmldKd"

# Load and Save Keys Functions
def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as file:
        json.dump(keys, file, indent=4)

# Key Generation
def generate_key_string():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# HWID Retrieval
def get_hwid():
    return hashlib.sha256(os.popen("wmic csproduct get uuid").read().encode()).hexdigest()

# Send Data to Discord
def send_to_discord(username, key, action, keys_left, hwid):
    embed_data = {
        "embeds": [
            {
                "title": f"Action Logged - {action}",
                "description": f"**Username**: {username}\n**Key Used**: {key}\n**HWID**: {hwid}\n**Action**: {action}\n**Keys Left**: {keys_left}",
                "color": 0xCB6CE6,
                "fields": [
                    {"name": "Username", "value": username, "inline": True},
                    {"name": "Key", "value": key, "inline": True},
                    {"name": "HWID", "value": hwid, "inline": True},
                    {"name": "Keys Left", "value": str(keys_left), "inline": True}
                ]
            }
        ]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=embed_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")

# Block/Unblock Roblox
def block_roblox(username, key):
    os.system("netsh advfirewall firewall add rule name='BlockRoblox' dir=out action=block remoteip=128.116.0.0/16")
    send_to_discord(username, key, "Start Dupe", user_keys.get(username, {}).get("keys_left", 0), get_hwid())

def unblock_roblox(username, key):
    os.system("netsh advfirewall firewall delete rule name='BlockRoblox'")
    send_to_discord(username, key, "End Dupe", user_keys.get(username, {}).get("keys_left", 0), get_hwid())

# Main App Class
class TactDupeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tact Dupe Tool")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1a1a1a; color: #ffffff; font-family: Arial;")

        self.user_keys = load_keys()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget()

        # Page 1 - Username Entry
        self.page1 = QWidget()
        self.page1_layout = QVBoxLayout()

        title_label = QLabel("Runeslayer Dupe", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; color: #CB6CE6; font-weight: bold;")
        self.page1_layout.addWidget(title_label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter your Username")
        self.username_input.setStyleSheet("background-color: #333333; border: 1px solid #CB6CE6; padding: 10px;")
        self.page1_layout.addWidget(self.username_input)

        generate_button = QPushButton("Generate Key", self)
        generate_button.setStyleSheet("background-color: #CB6CE6; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        generate_button.clicked.connect(self.generate_key)
        self.page1_layout.addWidget(generate_button)

        self.page1.setLayout(self.page1_layout)

        # Page 2 - Key Entry and Validation
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

        # Page 3 - Dupe Control (Block/Unblock Roblox)
        self.page3 = QWidget()
        self.page3_layout = QVBoxLayout()

        block_button = QPushButton("Block Roblox", self)
        block_button.setStyleSheet("background-color: #CB6CE6; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        block_button.clicked.connect(self.block_roblox)
        self.page3_layout.addWidget(block_button)

        unblock_button = QPushButton("Unblock Roblox", self)
        unblock_button.setStyleSheet("background-color: #CB6CE6; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        unblock_button.clicked.connect(self.unblock_roblox)
        self.page3_layout.addWidget(unblock_button)

        self.page3.setLayout(self.page3_layout)

        self.stacked_widget.addWidget(self.page1)  # Page 1: Username
        self.stacked_widget.addWidget(self.page2)  # Page 2: Key Entry
        self.stacked_widget.addWidget(self.page3)  # Page 3: Dupe Control

        self.layout.addWidget(self.stacked_widget)
        self.setLayout(self.layout)

    def generate_key(self):
        username = self.username_input.text().strip()
        current_hwid = get_hwid()

        if not username:
            QMessageBox.warning(self, "Error", "Please enter a valid username.")
            return

        if username in self.user_keys:
            saved_hwid = self.user_keys[username].get("hwid", "0")

            if saved_hwid == "0":  # First time setup
                self.user_keys[username]["hwid"] = current_hwid
                self.user_keys[username]["keys_left"] = 3  # Set initial keys left to 3
                save_keys(self.user_keys)
            elif saved_hwid != current_hwid:
                QMessageBox.warning(self, "Error", "HWID Mismatch! Please contact support.")
                return

            # Generate new key and update keys_left
            if self.user_keys[username]["keys_left"] > 0:
                key = generate_key_string()
                self.user_keys[username]["key"] = key
                self.user_keys[username]["keys_left"] -= 1
                save_keys(self.user_keys)

                send_to_discord(username, key, "Generated Key", self.user_keys[username]["keys_left"], current_hwid)

                self.stacked_widget.setCurrentIndex(1)  # Go to key entry page
            else:
                QMessageBox.warning(self, "Error", "You have no keys left!")
        else:
            QMessageBox.warning(self, "Error", "Username not found in keys!")

    def validate_key(self):
        username = self.username_input.text().strip()
        key = self.key_input.text().strip()

        if username in self.user_keys and self.user_keys[username]["key"] == key:
            QMessageBox.information(self, "Success", "Key validated successfully!")
            self.stacked_widget.setCurrentIndex(2)  # Go to dupe control page
        else:
            QMessageBox.warning(self, "Error", "Invalid key or username!")

    def block_roblox(self):
        username = self.username_input.text().strip()
        key = self.key_input.text().strip()

        if username in self.user_keys and self.user_keys[username]["key"] == key:
            block_roblox(username, key)
            QMessageBox.information(self, "Success", "Roblox blocked successfully.")
        else:
            QMessageBox.warning(self, "Error", "Invalid key or username!")

    def unblock_roblox(self):
        username = self.username_input.text().strip()
        key = self.key_input.text().strip()

        if username in self.user_keys and self.user_keys[username]["key"] == key:
            unblock_roblox(username, key)
            QMessageBox.information(self, "Success", "Roblox unblocked successfully.")
        else:
            QMessageBox.warning(self, "Error", "Invalid key or username!")

# Run the Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TactDupeApp()
    window.show()
    sys.exit(app.exec())
