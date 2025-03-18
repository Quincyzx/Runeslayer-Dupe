"""
Authentication utilities for Tact Tool
Handles HWID generation, license verification, and usage tracking
"""
import os
import json
import hashlib
import platform
import requests
import socket
import uuid
import getpass
import base64
from typing import Dict, Tuple, Optional

# GitHub Configuration
GITHUB_USER = "Quincyzx"
GITHUB_REPO = "Runeslayer-Dupe"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = "your_github_token_here"  # Replace with your actual token

def update_github_file(file_path: str, content: str, commit_message: str) -> Tuple[bool, str]:
    """Update a file in GitHub repository"""
    try:
        # GitHub API endpoint
        api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{file_path}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Get current file info
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            return False, f"Failed to get file info: {response.status_code}"

        file_info = response.json()
        current_sha = file_info.get('sha')

        # Prepare update data
        update_data = {
            "message": commit_message,
            "content": base64.b64encode(content.encode()).decode(),
            "sha": current_sha,
            "branch": GITHUB_BRANCH
        }

        # Update file
        response = requests.put(api_url, headers=headers, json=update_data)
        if response.status_code not in [200, 201]:
            return False, f"Failed to update file: {response.status_code}"

        return True, "File updated successfully"

    except Exception as e:
        return False, f"GitHub update error: {str(e)}"

def get_system_id() -> str:
    """Generate a unique system identifier"""
    try:
        # Get system information
        system_info = [
            platform.node(),
            platform.machine(),
            platform.processor(),
            getpass.getuser(),
            socket.gethostname()
        ]

        # Add Windows-specific identifiers
        if platform.system() == "Windows":
            try:
                import wmi
                c = wmi.WMI()
                system_info.extend([
                    c.Win32_Processor()[0].ProcessorId.strip(),
                    c.Win32_BIOS()[0].SerialNumber.strip(),
                    c.Win32_BaseBoard()[0].SerialNumber.strip()
                ])
            except:
                pass

        # Add Linux-specific identifiers
        elif platform.system() == "Linux":
            try:
                with open('/etc/machine-id', 'r') as f:
                    system_info.append(f.read().strip())
            except:
                pass

        # Add macOS-specific identifiers
        elif platform.system() == "Darwin":
            try:
                import subprocess
                result = subprocess.check_output(["system_profiler", "SPHardwareDataType"])
                system_info.append(result.decode())
            except:
                pass

        # Generate hash from system information
        system_id = hashlib.sha256('+'.join(system_info).encode()).hexdigest()
        return system_id

    except Exception as e:
        print(f"Error generating system ID: {e}")
        # Fallback to basic system info
        basic_info = [
            platform.node(),
            platform.machine(),
            getpass.getuser(),
            socket.gethostname()
        ]
        return hashlib.md5('+'.join(basic_info).encode()).hexdigest()

def verify_license(key: str, keys_file: str) -> Tuple[bool, Optional[Dict], str]:
    """Verify license key and check HWID"""
    try:
        # Read keys file
        with open(keys_file, 'r') as f:
            keys_data = json.load(f)

        # Find the key in the keys array
        key_entry = None
        for entry in keys_data.get('keys', []):
            if entry.get('key') == key:
                key_entry = entry
                break

        if not key_entry:
            return False, None, "Invalid license key"

        # Check uses remaining
        uses_remaining = key_entry.get('uses_remaining', 0)
        if uses_remaining <= 0:
            return False, None, "No uses remaining"

        # Get current system ID
        current_hwid = get_system_id()

        # Check HWID if registered
        registered_hwid = key_entry.get('hwid')
        if registered_hwid:
            if registered_hwid != current_hwid:
                return False, None, "Hardware ID mismatch"
        else:
            # Register HWID for new user
            key_entry['hwid'] = current_hwid

            # Save updated keys file locally
            with open(keys_file, 'w') as f:
                json.dump(keys_data, f, indent=4)

            # Update GitHub
            success, message = update_github_file(
                'keys.json',
                json.dumps(keys_data, indent=4),
                f"Update HWID for key: {key}"
            )
            if not success:
                print(f"Warning: Failed to update GitHub: {message}")

        return True, key_entry, "Success"

    except Exception as e:
        return False, None, f"Verification error: {str(e)}"

def update_usage(key: str, keys_file: str) -> Tuple[bool, str]:
    """Update usage count for license key"""
    try:
        # Read keys file
        with open(keys_file, 'r') as f:
            keys_data = json.load(f)

        # Find and update the key
        key_updated = False
        for entry in keys_data.get('keys', []):
            if entry.get('key') == key:
                entry['uses_remaining'] = max(0, entry.get('uses_remaining', 0) - 1)
                key_updated = True
                break

        if not key_updated:
            return False, "Invalid license key"

        # Save updated keys file locally
        with open(keys_file, 'w') as f:
            json.dump(keys_data, f, indent=4)

        # Update GitHub
        success, message = update_github_file(
            'keys.json',
            json.dumps(keys_data, indent=4),
            f"Update usage count for key: {key}"
        )
        if not success:
            print(f"Warning: Failed to update GitHub: {message}")

        return True, "Usage updated successfully"

    except Exception as e:
        return False, f"Update error: {str(e)}"
