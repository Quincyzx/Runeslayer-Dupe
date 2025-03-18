#!/usr/bin/env python3
"""
KeyAuth Client for RuneSlayer
A simple client for the KeyAuth authentication system
"""
import os
import json
import time
import hmac
import uuid
import hashlib
import platform
import subprocess
import requests

class KeyAuth:
    def __init__(self, name, ownerid, app_secret, version, api_url="https://keyauth.win/api/1.2/"):
        """
        Initialize the KeyAuth client
        
        :param name: Application name
        :param ownerid: Owner ID (from KeyAuth dashboard)
        :param app_secret: Application secret (from KeyAuth dashboard)
        :param version: Application version
        :param api_url: API URL (default: https://keyauth.win/api/1.2/)
        """
        self.name = name
        self.ownerid = ownerid
        self.app_secret = app_secret
        self.version = version
        self.api_url = api_url
        
        # Session data
        self.session_id = None
        self.initialized = False
        
        # User data
        self.user_data = {
            "username": "",
            "ip": "",
            "hwid": "",
            "expires": "",
            "createdate": "",
            "lastlogin": "",
            "subscription": ""
        }
        
        print(f"KeyAuth client initialized for application: {name}")
    
    def _get_hwid(self):
        """Get hardware ID of the current device"""
        if platform.system() == "Windows":
            return str(subprocess.check_output('wmic csproduct get uuid', shell=True).decode().split('\n')[1].strip())
        elif platform.system() == "Darwin":
            return str(uuid.uuid1())
        elif platform.system() == "Linux":
            try:
                with open('/etc/machine-id') as f:
                    return f.read().strip()
            except:
                return str(uuid.uuid1())
        else:
            return str(uuid.uuid1())
    
    def _make_request(self, endpoint, data=None):
        """Make a request to the KeyAuth API"""
        if data is None:
            data = {}
            
        # Add session ID if initialized
        if self.session_id:
            data["sessionid"] = self.session_id
            
        # Add standard parameters
        data["name"] = self.name
        data["ownerid"] = self.ownerid
        
        try:
            response = requests.post(
                f"{self.api_url}{endpoint}",
                data=data,
                timeout=30
            )
            
            # Parse response
            try:
                return response.json()
            except:
                print(f"ERROR: Invalid response from API: {response.text}")
                return {"success": False, "message": "Invalid API response"}
        except Exception as e:
            print(f"ERROR: Failed to make API request: {str(e)}")
            return {"success": False, "message": f"Request failed: {str(e)}"}
    
    def init(self):
        """Initialize the KeyAuth client"""
        print("Initializing KeyAuth client...")
        
        # Create data payload
        data = {
            "type": "init",
            "ver": self.version,
            "hash": hmac.new(
                self.app_secret.encode(),
                f"{self.name}{self.ownerid}{self.version}".encode(),
                hashlib.sha256
            ).hexdigest(),
            "enckey": "enckey",
            "hwid": self._get_hwid()
        }
        
        # Make request
        response = self._make_request("init", data)
        
        # Check if success
        if response.get("success"):
            # Save session ID
            self.session_id = response.get("sessionid")
            self.initialized = True
            print("KeyAuth initialized successfully")
            return True, "Initialized successfully"
        else:
            # Get error message
            message = response.get("message", "Unknown error")
            print(f"ERROR: Failed to initialize KeyAuth: {message}")
            return False, message
    
    def login(self, username, password):
        """Login with username and password"""
        print(f"Attempting to login with username: {username}")
        
        # Check if initialized
        if not self.initialized:
            print("ERROR: KeyAuth not initialized")
            return False, "KeyAuth not initialized"
        
        # Create data payload
        data = {
            "type": "login",
            "username": username,
            "password": password,
            "hwid": self._get_hwid()
        }
        
        # Make request
        response = self._make_request("login", data)
        
        # Check if success
        if response.get("success"):
            # Save user data
            self._update_user_data(response)
            print(f"Login successful for user: {username}")
            return True, "Login successful"
        else:
            # Get error message
            message = response.get("message", "Unknown error")
            print(f"ERROR: Login failed: {message}")
            return False, message
    
    def license(self, key):
        """Authenticate with a license key"""
        print("Attempting to authenticate with license key")
        
        # Check if initialized
        if not self.initialized:
            print("ERROR: KeyAuth not initialized")
            return False, "KeyAuth not initialized"
        
        # Create data payload
        data = {
            "type": "license",
            "key": key,
            "hwid": self._get_hwid()
        }
        
        # Make request
        response = self._make_request("license", data)
        
        # Check if success
        if response.get("success"):
            # Save user data
            self._update_user_data(response)
            print("License validation successful")
            return True, "License key verified"
        else:
            # Get error message
            message = response.get("message", "Unknown error")
            print(f"ERROR: License validation failed: {message}")
            return False, message
    
    def register(self, username, password, license_key):
        """Register a new user"""
        print(f"Attempting to register user: {username}")
        
        # Check if initialized
        if not self.initialized:
            print("ERROR: KeyAuth not initialized")
            return False, "KeyAuth not initialized"
        
        # Create data payload
        data = {
            "type": "register",
            "username": username,
            "password": password,
            "key": license_key,
            "hwid": self._get_hwid()
        }
        
        # Make request
        response = self._make_request("register", data)
        
        # Check if success
        if response.get("success"):
            # Save user data
            self._update_user_data(response)
            print(f"Registration successful for user: {username}")
            return True, "Registration successful"
        else:
            # Get error message
            message = response.get("message", "Unknown error")
            print(f"ERROR: Registration failed: {message}")
            return False, message
    
    def upgrade(self, username, license_key):
        """Upgrade a user's subscription"""
        print(f"Attempting to upgrade user: {username}")
        
        # Check if initialized
        if not self.initialized:
            print("ERROR: KeyAuth not initialized")
            return False, "KeyAuth not initialized"
        
        # Create data payload
        data = {
            "type": "upgrade",
            "username": username,
            "key": license_key
        }
        
        # Make request
        response = self._make_request("upgrade", data)
        
        # Check if success
        if response.get("success"):
            print(f"Upgrade successful for user: {username}")
            return True, "Upgrade successful"
        else:
            # Get error message
            message = response.get("message", "Unknown error")
            print(f"ERROR: Upgrade failed: {message}")
            return False, message
    
    def log(self, message):
        """Log a message to KeyAuth dashboard"""
        # Check if initialized
        if not self.initialized:
            print("ERROR: KeyAuth not initialized")
            return False, "KeyAuth not initialized"
        
        # Create data payload
        data = {
            "type": "log",
            "message": message,
            "pcuser": os.getenv('USERNAME', 'user'),
            "session": self.session_id
        }
        
        # Make request
        response = self._make_request("log", data)
        
        # Return success/failure
        return response.get("success", False), response.get("message", "Unknown error")
    
    def _update_user_data(self, response):
        """Update user data from response"""
        # Map response fields to user_data
        if "info" in response:
            info = response["info"]
            self.user_data = {
                "username": info.get("username", ""),
                "ip": info.get("ip", ""),
                "hwid": info.get("hwid", ""),
                "expires": info.get("expires", ""),
                "createdate": info.get("createdate", ""),
                "lastlogin": info.get("lastlogin", ""),
                "subscription": info.get("subscription", "")
            }
    
    def get_user_data(self):
        """Get the user data"""
        return self.user_data
