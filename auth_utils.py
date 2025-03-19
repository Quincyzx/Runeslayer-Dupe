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
from typing import Dict, Tuple, Optional, List

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

def verify_license(key: str, keys_file: str) -> Tuple[bool, Optional[Dict], str]:
    """Verify license key and check HWID"""
    try:
        # Check if file exists
        if not os.path.exists(keys_file):
            return False, None, "License database not found"
        
        # Load keys database
        with open(keys_file, 'r') as f:
            db = json.load(f)
        
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
        
        # If HWID is not set, set it now
        if 'hwid' not in user_data or not user_data['hwid']:
            db['keys'][key]['hwid'] = current_hwid
            with open(keys_file, 'w') as f:
                json.dump(db, f, indent=2)
        
        return True, user_data, "License verified successfully"
    
    except Exception as e:
        return False, None, f"Verification error: {str(e)}"

def update_usage(key: str, keys_file: str) -> Tuple[bool, str]:
    """Update usage count for license key"""
    try:
        # Check if file exists
        if not os.path.exists(keys_file):
            return False, "License database not found"
        
        # Load keys database
        with open(keys_file, 'r') as f:
            db = json.load(f)
        
        if 'keys' not in db or key not in db['keys']:
            return False, "Invalid license key"
        
        # Update usage count if it exists
        if 'uses_remaining' in db['keys'][key]:
            db['keys'][key]['uses_remaining'] -= 1
            
            # Save updated database
            with open(keys_file, 'w') as f:
                json.dump(db, f, indent=2)
            
            # In a real app, you would also update the remote copy
            # update_github_file("keys.json", json.dumps(db, indent=2), f"Update usage for {key}")
            
            return True, "Usage count updated"
        
        return True, "No usage count to update"
    
    except Exception as e:
        return False, f"Usage update error: {str(e)}"
