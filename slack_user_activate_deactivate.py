"""
Script: Slack User Activate + Deactivate

Description:
This script activates or deactivates Slack users based on user IDs provided either directly or from a CSV file. 
The script uses a SCIM token from the SlackOrgOwner App to perform the actions.

CSV File Structure:
- No headers required, each row should contain a user ID.

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- activate_user: Activates a user in Slack.
- deactivate_user: Deactivates a user in Slack.
- main: Main function to drive the script based on user input.

Usage:
1. Run the script.
2. Enter 'one' if you have one account or 'multiple' for multiple accounts.
3. If 'one', enter the user ID and the path to your SCIM access token file.
4. If 'multiple', enter the path to the CSV file containing user IDs and the path to your SCIM access token file.
5. Enter 'activate' or 'deactivate' to perform the action.
6. The script will process each user ID and activate or deactivate them in Slack.

Notes:
- Ensure that the SCIM token has the necessary permissions to activate or deactivate users.
- Handle the SCIM token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
import requests

def get_slack_token(token_path):
    """Reads the Slack token from a specified file.

    Args:
        token_path: The path to the file containing the Slack token.

    Returns:
        The Slack token as a string.
    """
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def activate_user(user_id, access_token):
    """Activates a user in Slack.

    Args:
        user_id: The ID of the user to activate.
        access_token: The SCIM access token.

    Returns:
        None
    """
    url = f"https://api.slack.com/scim/v1/Users/{user_id}"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        "active": True
    }
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"User ID {user_id} has been successfully activated.")
    else:
        print(f"Failed to activate user ID {user_id}. Status code: {response.status_code}")

def deactivate_user(user_id, access_token):
    """Deactivates a user in Slack.

    Args:
        user_id: The ID of the user to deactivate.
        access_token: The SCIM access token.

    Returns:
        None
    """
    url = f"https://api.slack.com/scim/v1/Users/{user_id}"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204 or response.text == '':
        print(f"User ID {user_id} has been successfully deactivated.")
    else:
        print(f"Failed to deactivate user ID {user_id}. Status code: {response.status_code}")

def main():
    """Main function to drive the script based on user input."""
    account_type = input("Enter 'one' if you have one account or 'multiple' for multiple accounts: ")

    if account_type == 'one':
        user_id = input("Enter the user ID: ")
        token_path = input("Please enter the path to your SCIM access token file: ")
        access_token = get_slack_token(token_path)
        
        action = input("Enter 'activate' or 'deactivate' to perform the action: ")
        
        if action == 'activate':
            activate_user(user_id, access_token)
        elif action == 'deactivate':
            deactivate_user(user_id, access_token)
        else:
            print("Invalid action. Please enter 'activate' or 'deactivate'.")
    else:
        csv_file = input("Enter the CSV file location: ")
        
        user_ids = []
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                user_ids.append(row[0])  # Assuming the user ID is in the first column
        
        token_path = input("Please enter the path to your SCIM access token file: ")
        access_token = get_slack_token(token_path)
        
        action = input("Enter 'activate' or 'deactivate' to perform the action: ")
        
        for user_id in user_ids:
            if action == 'activate':
                activate_user(user_id, access_token)
            elif action == 'deactivate':
                deactivate_user(user_id, access_token)
            else:
                print("Invalid action. Please enter 'activate' or 'deactivate'.")
                break

if __name__ == "__main__":
    main()
