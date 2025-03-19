"""
Authentication utilities for Tact Tool
Handles HWID generation, license verification, and usage tracking
"""
import os
import json
import datetime
import uuid
import socket
import platform
import requests
from typing import Dict, Tuple, Optional, List

GITHUB_RAW_URL = "https://raw.githubusercontent.com/<user>/<repo>/main/" # Replace with your GitHub raw URL

def update_github_file(file_path: str, content: str, commit_message: str) -> Tuple[bool, str]:
    """Update a file in GitHub repository"""
    try:
        # In real implementation, use GitHub API to update file
        # For this demo, just print the intent
        print(f"Would update GitHub file {file_path} with message: {commit_message}")
        return True, "Update simulated successfully"
    except Exception as e:
        return False, str(e)

def get_system_id() -> str:
    """Generate a unique system identifier"""
    try:
        # Get various system identifiers
        hostname = socket.gethostname()
        machine_id = str(uuid.getnode())  # MAC address as integer
        system_info = platform.system() + platform.version()

        # Combine and hash to create a unique but consistent identifier
        combined = f"{hostname}-{machine_id}-{system_info}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, combined))
    except:
        # Fallback to a random UUID if system info can't be retrieved
        return str(uuid.uuid4())

def verify_license(key: str, keys_file: str = "keys.json") -> Tuple[bool, Optional[Dict], str]:
    """Verify license key and check HWID"""
    try:
        # Load keys database from GitHub with timeout and error handling
        try:
            response = requests.get(f"{GITHUB_RAW_URL}{keys_file}", timeout=10)
            if response.status_code != 200:
                return False, None, f"Failed to load license database: HTTP {response.status_code}"
        except requests.Timeout:
            return False, None, "Connection timed out while loading license database"
        except requests.RequestException as e:
            return False, None, f"Network error: {str(e)}"
        db = response.json()

        if 'keys' not in db:
            return False, None, "Invalid license database format"

        # Check if key exists
        if key not in db['keys']:
            return False, None, "Invalid license key"

        user_data = db['keys'][key]

        # Check if license is expired
        if 'expires' in user_data:
            try:
                expiry_date = datetime.datetime.strptime(user_data['expires'], '%Y-%m-%d').date()
                today = datetime.datetime.now().date()
                if today > expiry_date:
                    return False, None, "License has expired"
            except:
                pass  # Skip expiry check if date format is invalid

        # Check if uses are exhausted
        if 'uses_remaining' in user_data and user_data['uses_remaining'] <= 0:
            return False, None, "License usage count exhausted"

        # Check HWID if it's set
        current_hwid = get_system_id()
        if 'hwid' in user_data and user_data['hwid'] and user_data['hwid'] != current_hwid:
            return False, None, "Hardware ID verification failed"

        # If HWID is not set, set it now.  This requires a GitHub API update, which is simulated.
        if 'hwid' not in user_data or not user_data['hwid']:
            user_data['hwid'] = current_hwid
            success, message = update_github_file(keys_file, json.dumps(db, indent=2), f"Update HWID for {key}")
            if not success:
                return False, None, f"Failed to update HWID: {message}"

        return True, user_data, "License verified successfully"

    except Exception as e:
        return False, None, f"Verification error: {str(e)}"

def update_usage(key: str, keys_file: str = "keys.json") -> Tuple[bool, str]:
    """Update usage count for license key"""
    try:
        # Load keys database from GitHub
        response = requests.get(f"{GITHUB_RAW_URL}{keys_file}")
        if response.status_code != 200:
            return False, "Failed to load license database"
        db = response.json()

        if 'keys' not in db or key not in db['keys']:
            return False, "Invalid license key"

        # Update usage count if it exists
        if 'uses_remaining' in db['keys'][key]:
            db['keys'][key]['uses_remaining'] -= 1

            # Save updated database to GitHub (simulated)
            success, message = update_github_file(keys_file, json.dumps(db, indent=2), f"Update usage for {key}")
            if not success:
                return False, f"Failed to update usage: {message}"

            return True, "Usage count updated"

        return True, "No usage count to update"

    except Exception as e:
        return False, f"Usage update error: {str(e)}"
