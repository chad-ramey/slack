"""
Script: Find Channel Name from ID

Description:
This script retrieves the name of a Slack channel using its channel ID. For private channels, 
ensure the bot is added to the channel and use the bot token, or add a user to the channel and use the user token.

Functions:
- Prompt the user for their Slack token file path and channel ID.
- Initialize the Slack WebClient.
- Call the `conversations.info` API method to retrieve channel information.
- Extract and display the channel name.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the Slack channel ID when prompted.
4. The script will display the name of the channel associated with the provided channel ID.

Notes:
- Ensure that the Slack token has the necessary permissions to access channel information.
- For private channels, the bot or user must be added to the channel.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import slack_sdk
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

# Ask the user for the path to their Slack token file
token_path = input("Please enter the path to your Slack token file: ")
token = get_slack_token(token_path)

# Ask the user for the channel ID
channel_id = input("Enter the channel ID: ")

# Initialize the Slack client
client = slack_sdk.WebClient(token=token)

try:
    # Use the conversations.info method to get information about the channel
    response = client.conversations_info(channel=channel_id)
    
    # Check if the API call was successful
    if response["ok"]:
        # Extract and print the channel name
        channel_name = response["channel"]["name"]
        print(f"Channel Name: {channel_name}")
    else:
        print("Error:", response["error"])
except SlackApiError as e:
    print(f"Error: {e.response['error']}")
