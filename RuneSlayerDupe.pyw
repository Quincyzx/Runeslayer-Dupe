import os
import sys
import requests
import json
import base64
import subprocess
import uuid

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

# Discord Webhook URL for logging
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1350911020146626784/F6QkaNdxIQCccpWtkBS6yrQykgsIG3j1B_ltAGARhJkGLObpiQCCwMSAtUDaLtSmldKd"

# Function to log errors to a file
def log_error(message):
    """Logs errors to a text file."""
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")
    print(message)  # Also print to console

# Get the SHA of the file (required for updating)
def get_sha_of_file():
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{KEYS_FILE_PATH}"
    try:
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
    except Exception as e:
        error_message = f"Exception getting SHA: {str(e)}"
        log_error(error_message)
        return None

# Download file from GitHub
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

    try:
        response = requests.put(api_url, json=data, headers=HEADERS)

        if response.status_code in (200, 201):
            print("Successfully updated keys.json on GitHub.")
            return True
        else:
            error_message = f"Error updating keys.json on GitHub: {response.status_code} - {response.text}"
            log_error(error_message)
            return False
    except Exception as e:
        error_message = f"Exception updating keys: {str(e)}"
        log_error(error_message)
        return False

# Get the HWID of the user
def get_hwid():
    hwid = uuid.UUID(int=uuid.getnode()).hex[-12:]  # Generate a simple HWID (MAC address-based)
    return hwid.upper()

# Send data to Discord webhook with different actions
def send_to_discord(username, keys_left, hwid, action, key_used=None):
    embeds = []
    
    # User Authentication Embed
    embeds.append({
        "title": "User Authentication",
        "description": f"**Username**: {username}\n**Keys Left**: {keys_left}\n**HWID**: {hwid}",
        "color": 0x00FF00,  # Green color for success
        "fields": [
            {"name": "Username", "value": username, "inline": True},
            {"name": "Keys Left", "value": str(keys_left), "inline": True},
            {"name": "HWID", "value": hwid, "inline": True}
        ]
    })
    
    # Action Logged - Generated Key Embed
    if action == "Generated Key":
        embeds.append({
            "title": "Action Logged - Generated Key",
            "description": f"**Username**: {username}\n**Key Used**: {key_used}\n**Action**: Generated Key",
            "color": 0xFFFF00,  # Yellow color for action
            "fields": [
                {"name": "Username", "value": username, "inline": True},
                {"name": "Key Used", "value": key_used, "inline": True},
                {"name": "Action", "value": "Generated Key", "inline": True}
            ]
        })
    
    # Action Logged - Key Validated Embed
    if action == "Key Validated":
        embeds.append({
            "title": "Action Logged - Key Validated",
            "description": f"**Username**: {username}\n**Key Used**: {key_used}\n**Action**: Key Validated",
            "color": 0x0000FF,  # Blue color for action
            "fields": [
                {"name": "Username", "value": username, "inline": True},
                {"name": "Key Used", "value": key_used, "inline": True},
                {"name": "Action", "value": "Key Validated", "inline": True}
            ]
        })

    embed_data = {"embeds": embeds}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=embed_data)
        response.raise_for_status()  # Raise an error for bad status codes
        return True
    except requests.exceptions.RequestException as e:
        error_message = f"Error sending to Discord: {e}"
        log_error(error_message)
        return False

# Run the downloaded script with username parameter
def run_script(username):
    """Runs the downloaded RuneSlayerDupe.pyw script with username parameter."""
    if os.path.exists(LOCAL_FILENAME):
        try:
            print(f"Running {LOCAL_FILENAME} for user {username}...")
            # Pass the username to the script
            subprocess.run([sys.executable, LOCAL_FILENAME, username], check=True)
            return True
        except subprocess.CalledProcessError as e:
            error_message = f"Error running the script: {e}"
            log_error(error_message)
            return False
    else:
        error_message = f"{LOCAL_FILENAME} not found! Please check the download process."
        log_error(error_message)
        return False

# Create a local config file to share data with the GUI
def save_local_config(username, keys_left):
    config = {
        "username": username,
        "keys_left": keys_left
    }
    try:
        with open("config.json", "w") as config_file:
            json.dump(config, config_file)
        return True
    except Exception as e:
        error_message = f"Error saving config: {e}"
        log_error(error_message)
        return False

# Main function for handling the process
def main():
    username = input("Enter username: ")
    hwid = get_hwid()  # Get the HWID of the system
    keys = load_keys()

    if keys:
        key_used = "VeoXAH5slELF"  # Example key
        current_keys_left = keys.get(key_used, 0)
        
        if current_keys_left == 0:
            keys[key_used] = 1  # Assign key count back
            send_to_discord(username, current_keys_left, hwid, "Generated Key", key_used)
        else:
            saved_hwid = keys.get(key_used, {}).get("hwid", "0")
            
            if saved_hwid == "0":
                keys[key_used]["hwid"] = hwid  # Store HWID in the JSON file
                send_to_discord(username, current_keys_left, hwid, "Key Validated", key_used)
            elif saved_hwid != hwid:
                send_to_discord(username, current_keys_left, hwid, "HWID Mismatch", key_used)

        # Update the keys JSON on GitHub
        sha = get_sha_of_file()
        if sha:
            save_keys_to_github(keys, sha)
        
        # Run the script
        run_script(username)
        save_local_config(username, current_keys_left)

# Run the program
if __name__ == "__main__":
    main()
