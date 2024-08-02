"""
Script: Slack Add or Remove Users from Channels

Description:
This script adds or removes users from one or more Slack channels based on data provided in a CSV file. 
The script can handle both public and private channels. For private channels, the Slack app needs to be 
a member, or another token created by a different admin/owner should be used.

CSV File Structure:
- The CSV file should contain headers: channel_id, users
- The 'users' column should contain a comma-separated list of user IDs.

Usage:
1. Install the Slack SDK using 'pip install slack_sdk'.
2. Run the script.
3. Enter the path to your Slack token file when prompted.
4. Provide the location of the CSV file containing channel IDs and user IDs.
5. Choose whether to 'add' or 'remove' users from channels.

Notes:
- Ensure that the Slack token has the necessary permissions to add or remove users from channels.
- The app must be a member of private channels to perform actions, or use a token from an admin/owner.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def main():
    # Prompt the user for the Slack token
    token_path = input("Please enter the path to your Slack token file: ")
    token = get_slack_token(token_path)

    # Prompt the user for the CSV location and header information
    csv_location = input("Enter the CSV location (channel_id,users): ")

    # Prompt the user to choose an action
    action = input("Do you want to 'add' or 'remove' users from channels? ").lower()

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
            retry = True
            while retry:
                try:
                    if action == 'add':
                        response = client.admin_conversations_invite(channel_id=channel_id, user_ids=[user_id])
                    elif action == 'remove':
                        response = client.conversations_kick(channel=channel_id, user=user_id)
                    else:
                        print("Invalid action. Please choose 'add' or 'remove'.")
                        break

                except SlackApiError as e:
                    if e.response.status_code == 429:  # Rate-limited error
                        print(f"Rate-limited. Retrying after {e.response.headers['Retry-After']} seconds...")
                        retry_after = int(e.response.headers['Retry-After'])
                        time.sleep(retry_after)
                    else:
                        print(f"Failed to perform action on User {user_id} for Channel {channel_id}: {e.response['error']}")
                    retry = False
                else:
                    if response['ok']:
                        print(f"User {user_id} was successfully {action}ed to/from Channel {channel_id}")
                    else:
                        print(f"Failed to perform action on User {user_id} for Channel {channel_id}: {response['error']}")
                    retry = False

if __name__ == "__main__":
    main()
