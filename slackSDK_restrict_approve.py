"""
Script: Slack Restrict or Approve App

Description:
This script allows administrators to either restrict or approve an app in a Slack workspace. The action 
(restrict or approve) is specified by the user, and the app is identified by its App ID and Team ID.

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- Main script block: Initializes the Slack WebClient and processes user input to restrict or approve an app.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Choose whether to restrict or approve an app.
4. Enter the App ID and Team ID when prompted.
5. The script will either restrict or approve the app based on the user's input.

Notes:
- Ensure that the Slack token has the necessary permissions to restrict or approve apps.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    """Reads the Slack token from a specified file.

    Args:
        token_path: The path to the file containing the Slack token.

    Returns:
        The Slack token as a string.
    """
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

# Initialize the Slack WebClient with your token
token_path = input("Please enter the path to your Slack token file: ")
token = get_slack_token(token_path)
client = WebClient(token=token)

# Get user input for action (restrict/approve)
action = input("Do you want to restrict or approve the app? (Type 'restrict' or 'approve'): ").lower()

if action == 'restrict':
    app_id = input("Enter the App ID: ")
    team_id = input("Enter the Team ID: ")
    try:
        response = client.admin_apps_restrict(app_id=app_id, team_id=team_id)
        print("App was restricted successfully!")
    except SlackApiError as e:
        print(f"Failed to restrict the app. Error: {e.response['error']}")
elif action == 'approve':
    app_id = input("Enter the App ID: ")
    team_id = input("Enter the Team ID: ")
    try:
        response = client.admin_apps_approve(app_id=app_id, team_id=team_id)
        print("App was approved successfully!")
    except SlackApiError as e:
        print(f"Failed to approve the app. Error: {e.response['error']}")
else:
    print("Invalid action. Please type 'restrict' or 'approve'.")
