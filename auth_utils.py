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
from typing import Dict, Tuple, Optional

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

            # Save updated keys file
            with open(keys_file, 'w') as f:
                json.dump(keys_data, f, indent=4)

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

        # Save updated keys file
        with open(keys_file, 'w') as f:
            json.dump(keys_data, f, indent=4)

        return True, "Usage updated successfully"

    except Exception as e:
        return False, f"Update error: {str(e)}"
