import os
import time
import json
import requests

# GitHub Repository Information
GITHUB_TOKEN = "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"  # Your GitHub token
KEYS_FILE_URL = "https://raw.githubusercontent.com/Quincyzx/Runeslayer-Dupe/main/keys.json"
KEYS_FILENAME = "keys.json"
LOCAL_FILENAME = "RuneSlayerDupe.pyw"
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

# Load keys from the downloaded keys.json file
def load_keys():
    """Loads the keys from GitHub if the local file doesn't exist."""
    try:
        print("Downloading keys.json from GitHub...")
        response = requests.get(KEYS_FILE_URL, headers=HEADERS)
        response.raise_for_status()
        with open(KEYS_FILENAME, "wb") as file:
            file.write(response.content)
        with open(KEYS_FILENAME, "r") as file:
            keys = json.load(file)
        print("Keys loaded successfully.")
        return keys
    except requests.exceptions.RequestException as e:
        error_message = f"Error downloading keys.json: {e}"
        log_error(error_message)
        return {}

# Check if the cooldown period is over
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

# Set the cooldown timestamp
def set_cooldown():
    """Sets the cooldown timestamp to prevent further use within the cooldown period."""
    current_time = time.time()
    with open(COOLDOWN_FILE, 'w') as file:
        file.write(str(current_time))

# Placeholder for the actual dupe action
def dupe_action():
    """Simulate the dupe action."""
    print("Performing the dupe action...")

# Main logic for the script
if __name__ == "__main__":
    # Step 1: Check if cooldown is active
    if not check_cooldown():
        print("Cooldown still active. Exiting.")
        exit(0)

    # Step 2: Load the keys and check for the user
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
            try:
                print("Saving updated keys.json to GitHub...")
                update_url = f"https://api.github.com/repos/Quincyzx/Runeslayer-Dupe/contents/keys.json"
                content = json.dumps(keys, indent=4)
                encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

                data = {
                    "message": "Update keys.json after performing dupe action",
                    "content": encoded_content,
                    "sha": keys.get("sha")
                }

                response = requests.put(update_url, json=data, headers=HEADERS)

                if response.status_code in (200, 201):
                    print("Successfully updated keys.json on GitHub.")
                else:
                    error_message = f"Error updating keys.json on GitHub: {response.status_code} - {response.text}"
                    log_error(error_message)
            except requests.exceptions.RequestException as e:
                error_message = f"Error saving keys.json to GitHub: {e}"
                log_error(error_message)

            # Step 4: Set the cooldown after successful action
            set_cooldown()
        else:
            print(f"No keys left for {username}. Cannot perform dupe.")
            log_error(f"No keys left for {username}. Cannot perform dupe.")
    else:
        print(f"Username {username} not found in keys.json.")
        log_error(f"Username {username} not found in keys.json.")
