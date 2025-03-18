import sys
import os
import requests
import hashlib
import uuid
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1350911020146626784/F6QkaNdxIQCccpWtkBS6yrQykgsIG3j1B_ltAGARhJkGLObpiQCCwMSAtUDaLtSmldKd"

# Function to get the hardware ID of the current machine
def get_hardware_id():
    try:
        system_uuid = str(uuid.uuid1()).encode()
        mac = uuid.getnode()
        mac_bytes = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2)).encode()
        computer_name = os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', '')).encode()
        combined = system_uuid + mac_bytes + computer_name
        hwid = hashlib.sha256(combined).hexdigest()
        return hwid
    except Exception as e:
        print(f"Error getting HWID: {e}")
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

# Function to send logs to Discord webhook with an embed
def send_to_discord_with_embed(username, key, action, hwid):
    embed_data = {
        "embeds": [
            {
                "title": f"Action Logged - {action}",
                "description": f"**Username**: {username}\n**Key Used**: {key}\n**Action**: {action}\n**HWID**: {hwid}",
                "color": 0xCB6CE6,
                "fields": [
                    {"name": "Username", "value": username, "inline": True},
                    {"name": "Key", "value": key, "inline": True},
                    {"name": "Action", "value": action, "inline": True},
                    {"name": "HWID", "value": hwid, "inline": False}
                ]
            }
        ]
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=embed_data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")
        return False

# Function to block Roblox
def block_roblox(username, key):
    os.system("netsh advfirewall firewall add rule name='BlockRoblox' dir=out action=block remoteip=128.116.0.0/16")
    print(f"Roblox connection blocked for {username} using key {key}!")
    send_to_discord_with_embed(username, key, "Start Dupe", get_hardware_id())

# Function to unblock Roblox
def unblock_roblox(username, key):
    os.system("netsh advfirewall firewall delete rule name='BlockRoblox'")
    print(f"Roblox connection restored for {username} using key {key}!")
    send_to_discord_with_embed(username, key, "End Dupe", get_hardware_id())
    # You would also handle the update_keys_left() function here.

class TactDupeTool(QWidget):
    def __init__(self, username, key):
        super().__init__()
        self.username = username
        self.key = key
        self.setWindowTitle("Tact RuneSlayer Dupe Tool")
        self.setFixedSize(200, 150)
        self.setStyleSheet("background-color: #1a1a1a; color: #ffffff; font-family: Arial;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        block_button = QPushButton("Block Roblox", self)
        block_button.setStyleSheet("background-color: #CB6CE6; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        block_button.clicked.connect(self.block)
        unblock_button = QPushButton("Unblock Roblox", self)
        unblock_button.setStyleSheet("background-color: #CB6CE6; color: #ffffff; border: none; padding: 10px; font-size: 14px;")
        unblock_button.clicked.connect(self.unblock)
        layout.addWidget(block_button)
        layout.addWidget(unblock_button)
        self.setLayout(layout)

    def block(self):
