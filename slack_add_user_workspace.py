"""
Script: Slack Add User to Workspace

Description:
This script adds users to a specified Slack workspace based on user IDs provided in a CSV file. 
The CSV file should contain a header 'user_id' with each row listing a user ID to be added to the workspace.

CSV File Structure:
- Headers: user_id

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- add_user_to_slack: Adds a user to the Slack workspace.
- main: Main function to drive the script based on user input.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the location of the CSV file containing user IDs.
4. Enter the Team ID for the Slack workspace.
5. The script will process each user ID and add them to the workspace.

Notes:
- Ensure that the Slack token has the necessary permissions to add users to the workspace.
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

def main():
    """Main function to drive the script based on user input."""
    token_path = input("Please enter the path to your Slack token file: ")
    token = get_slack_token(token_path)
    csv_location = input("Please enter the CSV file location: ")
    team_id = input("Please enter the Team ID for the workspace: ")

    with open(csv_location, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user_id = row.get('user_id')
            if user_id:
                response = add_user_to_slack(token, team_id, user_id)
                if response.status_code == 429:
                    print(f"Rate limited. Waiting for {response.headers['Retry-After']} seconds...")
                    time.sleep(int(response.headers['Retry-After']))
                    response = add_user_to_slack(token, team_id, user_id)

                if response.status_code == 200:
                    print(f"User {user_id} added to Slack workspace.")
                else:
                    print(f"Failed to add user {user_id}. Error: {response.text}")
            else:
                print("Missing user_id in the CSV row.")

if __name__ == "__main__":
    main()
