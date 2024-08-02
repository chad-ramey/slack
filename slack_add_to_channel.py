"""
Script: Slack Add User(s) to One or More Channels

Description:
This script adds users to specified Slack channels (both public and private) based on data provided in a CSV file. 
The CSV file should contain headers 'channel_id' and 'users', where 'users' is a comma-separated list of user IDs.

CSV File Structure:
- Headers: channel_id, users

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- Main script block: Reads user and channel data from a CSV file and adds the users to the channels, handling rate limiting.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the location of the CSV file containing channel IDs and user IDs.
4. The script will process each channel and user ID, adding the specified users to the channels.

Notes:
- Ensure that the Slack token has the necessary permissions to add users to channels.
- For private channels, the bot or user must be added to the channel.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
import time
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

# Prompt the user for the Slack token file path
token_path = input("Please enter the path to your Slack token file: ")
token = get_slack_token(token_path)

# Prompt the user for the CSV location and header information
csv_location = input("Please enter the CSV location (channel_id,users): ")

# Extract the data from the CSV
channels_data = []
with open(csv_location, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        channel_id = row['channel_id']
        users = row['users'].split(',')
        channels_data.append({'channel_id': channel_id, 'users': users})

client = WebClient(token=token)

for channel_data in channels_data:
    channel_id = channel_data['channel_id']
    users = channel_data['users']
    for user_id in users:
        payload = {
            'channel_id': channel_id,
            'user_ids': user_id
        }

        retry = True
        while retry:
            try:
                response = client.admin_conversations_invite(**payload)
            except SlackApiError as e:
                if e.response.status_code == 429:  # Rate-limited error
                    retry_after = int(e.response.headers['Retry-After'])
                    print(f"Rate-limited. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    print(f"Failed to add User {user_id} to Channel {channel_id}: {e.response['error']}")
                retry = False
            else:
                if response['ok']:
                    print(f"User {user_id} was successfully added to Channel {channel_id}")
                else:
                    print(f"Failed to add User {user_id} to Channel {channel_id}: {response['error']}")
                retry = False
