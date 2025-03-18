#!/usr/bin/env python3
"""
Utility functions for RuneSlayer
"""
import os
import sys
import uuid
import socket
import hashlib
import platform
import subprocess
from datetime import datetime

def get_hwid():
    """Generate a hardware ID based on system information"""
    if platform.system() == "Windows":
        try:
            # Try to get Windows UUID from wmic
            return str(subprocess.check_output('wmic csproduct get uuid', shell=True).decode().split('\n')[1].strip())
        except:
            # Fallback to machine-specific identifier
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()))
    elif platform.system() == "Darwin":
        try:
            # Try to get Mac serial number
            serial = subprocess.check_output("ioreg -c IOPlatformExpertDevice -d 2 | grep IOPlatformSerialNumber | sed -e 's/.*\"\\(.*\\)\"/\\1/'", shell=True).decode().strip()
            return hashlib.md5(serial.encode()).hexdigest()
        except:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()))
    elif platform.system() == "Linux":
        try:
            # Try to get machine-id
            with open('/etc/machine-id') as f:
                return f.read().strip()
        except:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()))
    else:
        # Fallback for unknown systems
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()))

def get_ip():
    """Get user's IP address"""
    try:
        # Connect to an external server to determine the public IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"

def create_dir_if_not_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_size(file_path):
    """Get size of a file in bytes"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

def get_file_checksum(file_path):
    """Calculate MD5 checksum of a file"""
    if not os.path.exists(file_path):
        return ""
        
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_valid_ip(ip):
    """Check if a string is a valid IP address"""
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

def is_valid_port(port):
    """Check if a string is a valid port number"""
    try:
        port_int = int(port)
        return 0 < port_int < 65536
    except:
        return False

def parse_proxy_string(proxy_string):
    """Parse a proxy string in the format ip:port"""
    if not proxy_string:
        return None, None
        
    parts = proxy_string.split(':')
    if len(parts) != 2:
        return None, None
        
    ip, port = parts
    if not is_valid_ip(ip) or not is_valid_port(port):
        return None, None
        
    return ip, int(port)
