"""
Script: Update Account to Multi-Channel with Activation

Description:
This script updates Slack accounts to multi-channel guest accounts with activation and attempts to keep Okta group memberships. 
It can process a single user or multiple users from a CSV file and optionally log API responses for debugging purposes.

CSV File Structure:
- The CSV file should contain headers: user_id

Functions:
- get_user_groups: Retrieves the groups a user belongs to.
- update_user: Updates a user to a multi-channel guest account and activates the account.
- readd_user_to_groups: Re-adds a user to their original groups after updating their account.

Usage:
1. Run the script.
2. Enter the path to your Slack SCIM API token file when prompted.
3. Choose whether to update one user or many users.
4. If updating many users, provide the path to the CSV file containing user IDs.
5. Optionally, enable API response checks for detailed output.

Notes:
- Ensure that the Slack token has the necessary permissions to update user accounts and manage group memberships.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import requests
import csv
import json

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def get_user_groups(user_id, token, enable_api_checks):
    """Retrieves the groups a user belongs to.

    Args:
        user_id: The ID of the user.
        token: The Slack SCIM API token.
        enable_api_checks: Boolean indicating whether to enable detailed API response checks.

    Returns:
        A list of groups the user belongs to.
    """
    url = f"https://api.slack.com/scim/v1/Users/{user_id}"
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if enable_api_checks:
        print(f"Get User Groups Response [{response.status_code}]: {response.text}")
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get("groups", [])
    else:
        print(f"Failed to get groups for user {user_id}. Status code: {response.status_code}")
        return []

def update_user(user_id, token, groups, enable_api_checks):
    """Updates a user to a multi-channel guest account and activates the account.

    Args:
        user_id: The ID of the user.
        token: The Slack SCIM API token.
        groups: The groups the user belongs to.
        enable_api_checks: Boolean indicating whether to enable detailed API response checks.
    """
    base_url = "https://api.slack.com/scim/v1/Users/"
    url = base_url + user_id
    payload = {
        "schemas": [
            "urn:scim:schemas:core:1.0",
            "urn:scim:schemas:extension:slack:guest:1.0"
        ],
        "active": True,
        "urn:scim:schemas:extension:slack:guest:1.0": {
            "type": "multi"
        },
        "groups": groups
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
        print(f"User {user_id} updated successfully. Account is now active.")
    else:
        print(f"Failed to update user {user_id}. Status code: {response.status_code}")

def readd_user_to_groups(user_id, token, groups, enable_api_checks):
    """Re-adds a user to their original groups after updating their account.

    Args:
        user_id: The ID of the user.
        token: The Slack SCIM API token.
        groups: The groups the user belongs to.
        enable_api_checks: Boolean indicating whether to enable detailed API response checks.
    """
    url = f"https://api.slack.com/scim/v1/Users/{user_id}"
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    payload = {
        "schemas": ["urn:scim:schemas:core:1.0"],
        "id": user_id,
        "groups": groups
    }

    if enable_api_checks:
        print(f"Re-adding User {user_id} to Groups Payload: {json.dumps(payload, indent=4)}")

    response = requests.patch(url, headers=headers, json=payload)
    if enable_api_checks:
        print(f"Re-add User to Groups Response [{response.status_code}]: {response.text}")
    if response.status_code == 200:
        print(f"User {user_id} re-added to groups successfully.")
    else:
        print(f"Failed to re-add user {user_id} to groups. Status code: {response.status_code}")

def main():
    """Main function to update users to multi-channel guest accounts and re-add them to their original groups."""
    token_path = input("Please enter the path to your Slack SCIM API token file: ")
    token = get_slack_token(token_path)
    user_choice = input("Do you want to update one user or many? (one/many): ").lower()
    enable_api_checks = input("Do you want to enable API Response Checks? (yes/no): ").lower() == 'yes'

    try:
        if user_choice == 'one':
            user_id = input("Enter the user ID: ")
            groups = get_user_groups(user_id, token, enable_api_checks)
            update_user(user_id, token, groups, enable_api_checks)
            readd_user_to_groups(user_id, token, groups, enable_api_checks)
        elif user_choice == 'many':
            csv_file = input("Enter the CSV file location (e.g., user_ids.csv): ")
            with open(csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    user_id = row['user_id']
                    groups = get_user_groups(user_id, token, enable_api_checks)
                    update_user(user_id, token, groups, enable_api_checks)
                    readd_user_to_groups(user_id, token, groups, enable_api_checks)
        else:
            print("Invalid choice. Please enter 'one' or 'many'.")
    except FileNotFoundError:
        print(f"CSV file '{csv_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
