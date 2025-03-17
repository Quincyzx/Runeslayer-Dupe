import os
import requests
import json
import base64
import subprocess
import sys
import time
import platform
import uuid
import hashlib

# GitHub Repository Information
GITHUB_TOKEN = "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"  # Your GitHub token
FILE_URL = "https://raw.githubusercontent.com/Quincyzx/Runeslayer-Dupe/main/RuneSlayerDupe.pyw"
KEYS_FILE_URL = "https://raw.githubusercontent.com/Quincyzx/Runeslayer-Dupe/main/keys.json"
LOCAL_FILENAME = "RuneSlayerDupe.pyw"
KEYS_FILENAME = "keys.json"
ICON_PATH = "Tact.ico"  # Ensure Tact.ico is in the same directory

# GitHub API URL to get file info
REPO_OWNER = "Quincyzx"
REPO_NAME = "Runeslayer-Dupe"
KEYS_FILE_PATH = "keys.json"  # Path to keys.json in the repo

# GitHub API Headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"  # Ensure we get JSON metadata
}

# File for cooldown tracking (hidden file location)
COOLDOWN_FILE = os.path.expanduser("~/.runeslayer_cooldown.txt")

# Webhook URL for sending results to Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1350911020146626784/F6QkaNdxIQCccpWtkBS6yrQykgsIG3j1B_ltAGARhJkGLObpiQCCwMSAtUDaLtSmldKd"

# Function to log errors to a file
def log_error(message):
    """Logs errors to a text file."""
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")

# Get the SHA of the file (required for updating)
def get_sha_of_file():
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{KEYS_FILE_PATH}"
    response = requests.get(api_url, headers=HEADERS)

    if response.status_code == 200:
        file_data = response.json()
        sha = file_data.get('sha')  # Get the SHA field from the response
        if sha:
            return sha
        else:
            error_message = f"SHA not found in response: {file_data}"
            log_error(error_message)
            return None
    else:
        error_message = f"Error getting file info: {response.status_code} - {response.text}"
        log_error(error_message)
        return None

# Download the keys.json file
def download_file(url, filename):
    """Downloads a file from GitHub."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an error for HTTP issues

        with open(filename, "wb") as file:
            file.write(response.content)

        print(f"Updated {filename} successfully.")
        return True
    except requests.exceptions.RequestException as e:
        error_message = f"Error downloading the file from GitHub: {e}"
        log_error(error_message)
        return False

# Load keys from the downloaded keys.json file
def load_keys():
    """Loads the keys from GitHub if the local file doesn't exist."""
    print("Checking for the latest keys.json from GitHub...")
    if download_file(KEYS_FILE_URL, KEYS_FILENAME):
        try:
            with open(KEYS_FILENAME, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            error_message = f"Error loading {KEYS_FILENAME}: {e}"
            log_error(error_message)
            return {}
    else:
        error_message = "Failed to download keys.json from GitHub."
        log_error(error_message)
        return {}

# Save the updated keys to GitHub
def save_keys_to_github(keys, sha):
    """Saves the updated keys to GitHub."""
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{KEYS_FILE_PATH}"

    # Prepare the content for the file
    content = json.dumps(keys, indent=4)
    
    # GitHub API requires Base64 encoded content
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": "Update keys.json with new data",
        "content": encoded_content,
        "sha": sha  # Use the retrieved SHA for the update
    }

    response = requests.put(api_url, json=data, headers=HEADERS)

    if response.status_code in (200, 201):
        print("Successfully updated keys.json on GitHub.")
        return True
    else:
        error_message = f"Error updating keys.json on GitHub: {response.status_code} - {response.text}"
        log_error(error_message)
        return False

# Download the latest version of RuneSlayerDupe.pyw
def download_latest_version():
    """Downloads the latest version of RuneSlayerDupe.pyw from GitHub."""
    return download_file(FILE_URL, LOCAL_FILENAME)

# Run the downloaded script
def run_script():
    """Runs the downloaded RuneSlayerDupe.pyw script."""
    if os.path.exists(LOCAL_FILENAME):
        try:
            print(f"Running {LOCAL_FILENAME}...")
            # Use pythonw.exe to prevent the console from opening
            subprocess.run([sys.executable.replace("python.exe", "pythonw.exe"), LOCAL_FILENAME], check=True)
            return True
        except subprocess.CalledProcessError as e:
            error_message = f"Error running the script: {e}"
            log_error(error_message)
            return False
    else:
        error_message = f"{LOCAL_FILENAME} not found! Please check the download process."
        log_error(error_message)
        return False

# Get the actual HWID of the machine
def get_hwid():
    """Returns the HWID of the system as a SHA-256 hash of the UUID."""
    try:
        # Use the WMIC command to fetch the system's UUID
        hwid_raw = subprocess.check_output("wmic csproduct get uuid").decode().split("\n")[1].strip()
        if hwid_raw:
            return hashlib.sha256(hwid_raw.encode()).hexdigest()
        else:
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    except Exception as e:
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

# Function to check if cooldown is still active
def check_cooldown():
    """Checks if the cooldown period has passed since last use."""
    if os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, 'r') as file:
            last_used = float(file.read().strip())
        current_time = time.time()
        cooldown_period = 8 * 60  # 8 minutes cooldown
        if current_time - last_used < cooldown_period:
            remaining_time = cooldown_period - (current_time - last_used)
            print(f"Cooldown is still active. Please wait {remaining_time / 60:.2f} minutes.")
            return False
    return True

# Function to set cooldown
def set_cooldown():
    """Sets the cooldown timestamp to prevent further use within the cooldown period."""
    current_time = time.time()
    with open(COOLDOWN_FILE, 'w') as file:
        file.write(str(current_time))

# Send to Webhook
def send_to_webhook(username, key):
    """Send the result to the Discord webhook."""
    data = {
        "content": f"Username: {username}\nKey: {key}\nHWID: {get_hwid()}"
    }
    response = requests.post(WEBHOOK_URL, json=data)
    return response.status_code == 204

# Main script
def main():
    # Check if cooldown is active
    if not check_cooldown():
        sys.exit()  # Exit if cooldown is active

    # Prompt for username input
    username = input("Enter the username: ")

    # Load the current keys from GitHub
    keys = load_keys()

    # Check if the username exists in the keys
    if username in keys:
        # Get the SHA of the current keys.json on GitHub (before modifying)
        sha = get_sha_of_file()

        if sha:
            current_keys_left = keys[username]["keys_left"]
            print(f"Original keys_left for {username}: {current_keys_left}")
            
            # Ensure the keys_left value is valid
            if current_keys_left > 0:
                new_keys_left = current_keys_left - 1  # Decrease by 1
            else:
                new_keys_left = current_keys_left  # If no keys are left, don't decrement
            
            # Update the hwid with the real machine's HWID
            hwid = get_hwid()
            keys[username]["hwid"] = hwid
            keys[username]["keys_left"] = new_keys_left  # Update the value
            print(f"Updated keys_left for {username}: {new_keys_left}")  # Print updated value
            print(f"Updated HWID for {username}: {hwid}")

            # Save the updated keys back to GitHub
            save_keys_to_github(keys, sha)

            # Perform the dupe action here
            print(f"Performing the dupe action for {username}...")
            # Dupe action logic goes here (You can customize this part)
            send_to_webhook(username, "Dupe successful")  # Example webhook action

            # Download the latest version of the script
            if download_latest_version():
                # Run the downloaded script
                run_script()

            # Set cooldown after the action is complete
            set_cooldown()

        else:
            error_message = "Failed to get SHA for keys.json. Cannot update the file."
            log_error(error_message)
    else:
        error_message = f"Error: '{username}' key not found in keys.json"
        log_error(error_message)

if __name__ == "__main__":
    main()
