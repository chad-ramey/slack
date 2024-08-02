"""
Script: Update Account to Multi-Channel Guest

Description:
This script updates Slack accounts to multi-channel guest accounts using the Slack SCIM API. 
The user can choose to update a single account or multiple accounts specified in a CSV file. 
Optional API response checks can be enabled for debugging purposes.

CSV File Structure:
- The CSV file should contain headers: user_id

Usage:
1. Run the script.
2. Enter the path to your Slack SCIM API token file when prompted.
3. Choose whether to update one user or many users.
4. If updating many users, provide the path to the CSV file containing user IDs.
5. Optionally, enable API response checks for detailed output.

Notes:
- Ensure that the Slack token has the necessary permissions to update user accounts.
- Handle the Slack token securely and do not expose it in the code.
- Customize the output and logging as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import requests
import csv
import json

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def update_user_to_multi_channel_guest(user_id, token, enable_api_checks):
    """Updates a user to a multi-channel guest account.

    Args:
        user_id: The ID of the user to update.
        token: The Slack SCIM API token.
        enable_api_checks: Boolean indicating whether to enable detailed API response checks.
    """
    url = f"https://api.slack.com/scim/v1/Users/{user_id}"
    payload = {
        "schemas": [
            "urn:scim:schemas:core:1.0",
            "urn:scim:schemas:extension:slack:guest:1.0"
        ],
        "active": True,
        "urn:scim:schemas:extension:slack:guest:1.0": {
            "type": "multi"
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    if enable_api_checks:
        print(f"Payload for User {user_id}: {json.dumps(payload, indent=4)}")

    response = requests.patch(url, headers=headers, json=payload)
    if enable_api_checks:
        print(f"Update User Response [{response.status_code}]: {response.text}")
    if response.status_code == 200:
        print(f"User {user_id} updated successfully to multi-channel guest.")
    else:
        print(f"Failed to update user {user_id}. Status code: {response.status_code}")

def main():
    # Prompt the user for the Slack SCIM API token
    token_path = input("Please enter the path to your Slack SCIM API token file: ")
    token = get_slack_token(token_path)

    # Prompt the user to choose whether to update one user or many
    user_choice = input("Do you want to update one user or many? (one/many): ").lower()

    # Prompt the user to enable or disable API response checks
    enable_api_checks = input("Do you want to enable API Response Checks? (yes/no): ").lower() == 'yes'

    try:
        if user_choice == 'one':
            user_id = input("Enter the user ID: ")
            update_user_to_multi_channel_guest(user_id, token, enable_api_checks)
        elif user_choice == 'many':
            csv_file = input("Enter the CSV file location (e.g., user_ids.csv): ")
            with open(csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    user_id = row['user_id']
                    update_user_to_multi_channel_guest(user_id, token, enable_api_checks)
        else:
            print("Invalid choice. Please enter 'one' or 'many'.")
    except FileNotFoundError:
        print(f"CSV file '{csv_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
