import requests
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget
from PySide6.QtCore import Qt
import string
import random
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

# Dictionary to store username and generated key
generated_keys = {}

# Function to generate a random key (based on username)
def generate_key_from_username(username):
    random.seed(username)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# Function to send logs to Discord webhook with an embed
def send_to_discord_with_embed(username, key, action):
    webhook_url = "https://discord.com/api/webhooks/1350911020146626784/F6QkaNdxIQCccpWtkBS6yrQykgsIG3j1B_ltAGARhJkGLObpiQCCwMSAtUDaLtSmldKd"
    
    embed_data = {
        "embeds": [
            {
                "title": f"Action Logged - {action}",
                "description": f"**Username**: {username}\n**Key Used**: {key}\n**Action**: {action}",
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
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=embed_data)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")
        return False  # Return false if the webhook fails
    return True  # Return true if the webhook is successful

# Function to block Roblox (simulate disconnect)
def block_roblox(username, key):
    os.system("netsh advfirewall firewall add rule name='BlockRoblox' dir=out action=block remoteip=128.116.0.0/16")
    print(f"Roblox connection blocked for {username} using key {key}!")  # Simulate the Roblox blocking
    send_to_discord_with_embed(username, key, "Start Dupe")

# Function to unblock Roblox (simulate reconnect)
def unblock_roblox(username, key):
    os.system("netsh advfirewall firewall delete rule name='BlockRoblox'")
    print(f"Roblox connection restored for {username} using key {key}!")  # Simulate the Roblox reconnect
    send_to_discord_with_embed(username, key, "End Dupe")

class TactDupeApp(QWidget):
    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle("Tact RuneSlayer Dupe")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1a1a1a; color: #ffffff; font-family: Arial;")

        self.init_ui()

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

        # Generate a key based on the username
        key = generate_key_from_username(username)
        generated_keys[username] = key  # Store the generated key with the username
        print(f"Generated key for {username}: {key}")

        # Send key and username to Discord with embed
        if send_to_discord_with_embed(username, key, "Generated Key"):
            # Move to the next page if the webhook is successful
            self.stacked_widget.setCurrentIndex(1)  # Switch to the next page for key entry
        else:
            QMessageBox.warning(self, "Error", "Failed to send data to Discord. Please check your connection.")

    def validate_key(self):
        entered_key = self.key_input.text()
        username = self.username_input.text()

        if not entered_key:
            QMessageBox.warning(self, "Validation Error", "Please enter the key.")
            return

        # Validate the entered key against the generated key for that username
        if generated_keys.get(username) == entered_key:
            QMessageBox.information(self, "Success", "Key validated successfully!")
            self.stacked_widget.setCurrentIndex(2)  # Switch to the dupe functionality page
        else:
            QMessageBox.warning(self, "Validation Error", "Invalid key entered. Please check your key and try again.")

    def block_roblox(self):
        username = self.username_input.text()
        key = self.key_input.text()
        block_roblox(username, key)  # Call the block_roblox function

    def unblock_roblox(self):
        username = self.username_input.text()
        key = self.key_input.text()
        unblock_roblox(username, key)  # Call the unblock_roblox function

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = TactDupeApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
