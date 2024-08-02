"""
Script: Slack Find Email Address from User ID

Description:
This script finds the email address associated with a Slack user ID using the Slack API.

Functions:
- Prompt the user for their Slack token file path and user ID.
- Initialize the Slack WebClient.
- Call the `users.info` API method to retrieve user information.
- Extract and display the email address from the user profile.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the Slack user ID when prompted.
4. The script will display the email address associated with the provided user ID.

Notes:
- Ensure that the Slack token has the necessary permissions to access user information.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

# Ask the user for the path to their Slack token file
token_path = input("Please enter the path to your Slack token file: ")
slack_token = get_slack_token(token_path)

# Ask the user for the Slack user ID
user_id = input("Enter the user ID: ")

# Initialize the Slack WebClient
client = WebClient(token=slack_token)

try:
    # Call the users.info API to get user information
    response = client.users_info(user=user_id)

    # Check if the API call was successful
    if response["ok"]:
        user_info = response["user"]
        email = user_info["profile"]["email"]
        print(f"User's email: {email}")
    else:
        print(f"Error: {response['error']}")

except SlackApiError as e:
    print(f"Error: {e.response['error']}")

except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
