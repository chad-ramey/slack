"""
Script: Slack Set Guest Expiration

Description:
This script sets expiration dates for guest users in Slack using the Slack API. 
The expiration date is provided as an epoch timestamp. Users can update expiration dates for one or multiple accounts.

Functions:
- Initialize the Slack SDK client with a token and team ID.
- Set expiration dates for one or multiple guest user accounts.

Usage:
1. Run the script.
2. Enter the path to your Slack API token file when prompted.
3. Enter your Slack Team ID when prompted.
4. Choose whether to update one or multiple accounts.
5. Provide the user ID(s) and the expiration timestamp.

Notes:
- Ensure that the Slack token has the necessary permissions to set expiration dates for users.
- Handle the Slack token securely and do not expose it in the code.
- The expiration timestamp should be provided in epoch time format.
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

# Ask the user for the path to their Slack API token file
token_path = input("Please enter the path to your Slack API token file: ")
token = get_slack_token(token_path)

# Ask the user for their Team ID
team_id = input("Please enter your Slack Team ID: ")

# Initialize the Slack API client
client = WebClient(token=token)

# Ask the user if they want to update one or more accounts
update_multiple = input("Do you want to update multiple accounts? (yes/no): ").strip().lower()

if update_multiple == "yes":
    # Ask the user for a comma-separated list of user IDs
    user_ids_input = input("Enter a comma-separated list of user IDs to update: ")
    user_ids = [user_id.strip() for user_id in user_ids_input.split(",")]
else:
    # Ask the user for a single user ID
    user_id = input("Enter the user ID to update: ")
    user_ids = [user_id]

# Set the expiration timestamp
expiration_ts = input("Enter the expiration timestamp (epoch time): ")

# Call the admin.users.setExpiration method for each user ID
for user_id in user_ids:
    try:
        response = client.admin_users_setExpiration(
            user_id=user_id,
            expiration_ts=expiration_ts,
            team_id=team_id
        )
        if response["ok"]:
            print(f"User {user_id} expiration set successfully.")
        else:
            print(f"Error for user {user_id}: {response['error']}")
    except SlackApiError as e:
        if "team_id_required_for_enterprise" in str(e):
            print(f"Error for user {user_id}: Team ID is required for enterprise accounts.")
        else:
            print(f"An error occurred for user {user_id}: {e.response['error']}")
