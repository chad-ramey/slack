"""
Script: Slack Add + Remove User from Workspace

Description:
This script adds or removes users from a Slack workspace based on user IDs provided in a CSV file. 
The action can be specified as either 'add' or 'remove'. The script handles rate limiting by waiting 
before retrying API requests.

CSV File Structure:
- The CSV file should contain a header: user_id

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- add_user_to_slack: Adds a user to the Slack workspace.
- remove_user_from_slack: Removes a user from the Slack workspace.
- main: Main function to drive the script based on user input.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the location of the CSV file containing user IDs.
4. Enter the Team ID for the Slack workspace.
5. Choose whether to 'add' or 'remove' users from the workspace.
6. The script will process each user ID and add or remove them from the workspace.

Notes:
- Ensure that the Slack token has the necessary permissions to add or remove users.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import requests
import csv
import time

def get_slack_token(token_path):
    """Reads the Slack token from a specified file.

    Args:
        token_path: The path to the file containing the Slack token.

    Returns:
        The Slack token as a string.
    """
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def add_user_to_slack(token, team_id, user_id):
    """Adds a user to the Slack workspace.

    Args:
        token: The Slack API token.
        team_id: The ID of the Slack team (workspace).
        user_id: The ID of the user to add.

    Returns:
        The response from the Slack API.
    """
    url = "https://slack.com/api/admin.users.assign"
    payload = f'team_id={team_id}&user_id={user_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(url, headers=headers, data=payload)
    return response

def remove_user_from_slack(token, team_id, user_id):
    """Removes a user from the Slack workspace.

    Args:
        token: The Slack API token.
        team_id: The ID of the Slack team (workspace).
        user_id: The ID of the user to remove.

    Returns:
        The response from the Slack API.
    """
    url = "https://slack.com/api/admin.users.remove"
    payload = f'team_id={team_id}&user_id={user_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(url, headers=headers, data=payload)
    return response

def main():
    """Main function to drive the script based on user input."""
    token_path = input("Please enter the path to your Slack token file: ")
    token = get_slack_token(token_path)
    csv_location = input("Please enter the CSV file location: ")
    team_id = input("Please enter the Team ID for the workspace: ")
    
    action = input("Do you want to 'add' or 'remove' users from the workspace? ").lower()

    if action not in ['add', 'remove']:
        print("Invalid action. Please choose 'add' or 'remove'.")
        return

    with open(csv_location, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user_id = row.get('user_id')
            if user_id:
                if action == 'add':
                    response = add_user_to_slack(token, team_id, user_id)
                elif action == 'remove':
                    response = remove_user_from_slack(token, team_id, user_id)

                if response.status_code == 429:
                    print(f"Rate limited. Waiting for {response.headers['Retry-After']} seconds...")
                    time.sleep(int(response.headers['Retry-After']))
                    if action == 'add':
                        response = add_user_to_slack(token, team_id, user_id)
                    elif action == 'remove':
                        response = remove_user_from_slack(token, team_id, user_id)

                if response.status_code == 200:
                    print(f"User {user_id} {action}ed from Slack workspace.")
                else:
                    print(f"Failed to {action} user {user_id}. Error: {response.text}")
            else:
                print("Missing user_id in the CSV row.")

if __name__ == "__main__":
    main()
