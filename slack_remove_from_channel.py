"""
Script: Slack Remove User(s) from One or More Channels

Description:
This script removes users from specified Slack channels based on data provided in a CSV file. 
For public channels, the script will work directly. For private channels, ensure the app is a member 
of those channels.

CSV File Structure:
- Headers: channel_id, users
- Each row should contain a channel ID and a comma-separated list of user IDs.

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- Main script block: Reads user and channel data from a CSV file and removes the users from the channels.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the location of the CSV file containing channel IDs and user IDs.
4. The script will process each channel and user ID, removing the specified users from the channels.

Notes:
- Ensure that the Slack token has the necessary permissions to remove users from channels.
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

# Initialize the Slack WebClient
client = WebClient(token=token)

for channel_data in channels_data:
    channel_id = channel_data['channel_id']
    users = channel_data['users']
    for user_id in users:
        retry = True
        while retry:
            try:
                response = client.conversations_kick(channel=channel_id, user=user_id)
            except SlackApiError as e:
                if e.response.status_code == 429:  # Rate-limited error
                    print(f"Rate-limited. Retrying after {e.response.headers['Retry-After']} seconds...")
                    retry_after = int(e.response.headers['Retry-After'])
                    time.sleep(retry_after)
                else:
                    print(f"Failed to remove User {user_id} from Channel {channel_id}: {e.response['error']}")
                retry = False
            else:
                if response['ok']:
                    print(f"User {user_id} was successfully removed from Channel {channel_id}")
                else:
                    print(f"Failed to remove User {user_id} from Channel {channel_id}: {response['error']}")
                retry = False
