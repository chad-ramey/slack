"""
Script: Slack Update User Profile for Out of Office/Vacation

Description:
This script updates a user's Slack profile to reflect their out-of-office or vacation status. 
It sets the user's display name, status text, status emoji, and status expiration.

Functions:
- get_slack_token: Reads the Slack token from a specified file.

Usage:
1. Run the script.
2. Enter the path to your Slack access token file when prompted.
3. Enter the user ID, display name, status text, status emoji, and status expiration.
4. The script will update the user's profile with the provided information.

Notes:
- Ensure that the Slack token has the necessary permissions to update user profiles.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

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

url = "https://slack.com/api/users.profile.set"

# Prompt the user for input
token_path = input("Please enter the path to your Slack access token file: ")
access_token = get_slack_token(token_path)
user_id = input("Enter user ID: ")
display_name = input("Enter display name: ")
status_text = input("Enter status text: ")
status_emoji = input("Enter status emoji: ")
status_expiration = input("Enter status expiration (Unix Time - 0 for indefinite): ")

# Prepare the payload for the API request
payload = {
    'profile': {
        'display_name': display_name,
        'status_text': status_text,
        'status_emoji': status_emoji,
        'status_expiration': int(status_expiration)
    },
    'user': user_id
}

# Set the request headers
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Send the API request to update the user's profile
response = requests.post(url, headers=headers, json=payload)

# Parse the response
data = response.json()

# Check if the request was successful
if response.ok and data.get('ok'):
    print("Status changes were successfully updated.")
else:
    print("Failed to update status changes.")
    if data.get('error'):
        print("Error message:", data['error'])
