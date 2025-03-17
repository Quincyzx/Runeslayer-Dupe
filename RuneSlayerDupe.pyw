import os
import time
import json
import requests
import base64

# GitHub Repository Information
GITHUB_TOKEN = "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"  # Your GitHub token
KEYS_FILE_URL = "https://raw.githubusercontent.com/Quincyzx/Runeslayer-Dupe/main/keys.json"
KEYS_FILENAME = "keys.json"
COOLDOWN_FILE = os.path.expanduser("~/.runeslayer_cooldown.txt")

# GitHub API Headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to log errors to a file
def log_error(message):
    """Logs errors to a text file."""
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")

# Function to download keys.json from GitHub
def download_keys():
    """Downloads the keys.json file from GitHub."""
    try:
        print("Downloading keys.json from GitHub...")
        response = requests.get(KEYS_FILE_URL, headers=HEADERS)
        response.raise_for_status()

        with open(KEYS_FILENAME, "wb") as file:
            file.write(response.content)
        print("keys.json downloaded successfully.")
    except requests.exceptions.RequestException as e:
        log_error(f"Error downloading keys.json: {e}")

# Function to load keys from the downloaded keys.json file
def load_keys():
    """Loads the keys from the downloaded keys.json file."""
    try:
        with open(KEYS_FILENAME, "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        log_error(f"Error loading {KEYS_FILENAME}: {e}")
        return {}

# Function to perform the dupe action
def dupe_action():
    """Simulates the dupe action."""
    print("Performing the dupe action...")

# Function to save the updated keys back to GitHub
def save_keys_to_github(keys):
    """Saves the updated keys back to GitHub."""
    try:
        print("Saving updated keys.json to GitHub...")
        update_url = f"https://api.github.com/repos/Quincyzx/Runeslayer-Dupe/contents/keys.json"
        content = json.dumps(keys, indent=4)
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        data = {
            "message": "Update keys.json after performing dupe action",
            "content": encoded_content
        }

        response = requests.put(update_url, json=data, headers=HEADERS)

        if response.status_code in (200, 201):
            print("Successfully updated keys.json on GitHub.")
        else:
            log_error(f"Error updating keys.json on GitHub: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        log_error(f"Error saving keys.json to GitHub: {e}")

# Main logic for the script
if __name__ == "__main__":
    try:
        # Step 1: Download keys.json if not already downloaded
        if not os.path.exists(KEYS_FILENAME):
            download_keys()

        # Step 2: Load the keys from the downloaded keys.json file
        keys = load_keys()

        # Prompt for username input
        username = input("Enter the username to perform the dupe: ")

        if username in keys:
            print(f"Found {username} in keys.json")
            current_keys_left = keys[username].get("keys_left", 0)
            print(f"Keys left for {username}: {current_keys_left}")

            # Ensure the keys_left is greater than 0 before performing the dupe
            if current_keys_left > 0:
                print(f"Performing dupe action for {username}...")
                dupe_action()

                # Decrease the keys_left by 1
                keys[username]["keys_left"] = current_keys_left - 1
                print(f"Updated keys_left for {username}: {keys[username]['keys_left']}")

                # Step 3: Save the updated keys back to GitHub
                save_keys_to_github(keys)
            else:
                print(f"No keys left for {username}. Cannot perform dupe.")
                log_error(f"No keys left for {username}. Cannot perform dupe.")
        else:
            print(f"Username {username} not found in keys.json.")
            log_error(f"Username {username} not found in keys.json.")

    except Exception as e:
        log_error(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")
