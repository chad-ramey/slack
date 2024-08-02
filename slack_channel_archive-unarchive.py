"""
Script: Slack Channel Archive + Unarchive

Description:
This script archives or unarchives Slack channels based on user input. It supports updating one, a few, or many channels, 
with the ability to mix statuses (archive/unarchive) when processing many channels from a CSV file.

CSV File Structure:
- The CSV file should contain headers: channel_id, channel_status
- The channel_status should be either 'archive' or 'unarchive'

Functions:
- archive_channels: Archives the specified channels.
- unarchive_channels: Unarchives the specified channels.
- get_channel_ids_from_user: Prompts the user to enter channel IDs.
- process_channels_from_csv: Processes channels from a CSV file based on the specified status.

Usage:
1. Run the script.
2. Enter the path to your Slack access token file when prompted.
3. Choose whether to update one, a few, or many channels.
4. For 'one' or 'few', enter the channel IDs and specify whether to archive or unarchive them.
5. For 'many', provide the path to a CSV file containing channel IDs and their statuses.

Notes:
- Ensure that the Slack token has the necessary permissions to archive or unarchive channels.
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
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def archive_channels(channel_ids, slack_client):
    """Archives the specified channels.

    Args:
        channel_ids: A list of channel IDs to be archived.
        slack_client: An instance of the Slack WebClient.
    """
    for channel_id in channel_ids:
        try:
            response = slack_client.admin_conversations_archive(channel_id=channel_id)
            print(f"Channel {channel_id} archived: {response['ok']}")
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers['Retry-After'])
                print(f"Rate-limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"Error: {e.response['error']} - {e.response['detail']}")

def unarchive_channels(channel_ids, slack_client):
    """Unarchives the specified channels.

    Args:
        channel_ids: A list of channel IDs to be unarchived.
        slack_client: An instance of the Slack WebClient.
    """
    for channel_id in channel_ids:
        try:
            response = slack_client.admin_conversations_unarchive(channel_id=channel_id)
            print(f"Channel {channel_id} unarchived: {response['ok']}")
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers['Retry-After'])
                print(f"Rate-limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"Error: {e.response['error']} - {e.response['detail']}")

def get_channel_ids_from_user(max_channels=10):
    """Prompts the user to enter channel IDs.

    Args:
        max_channels: The maximum number of channel IDs to prompt for.

    Returns:
        A list of entered channel IDs.
    """
    if max_channels == 1:
        return [input("Enter the channel ID: ").strip()]
    else:
        channel_ids = input(f"Enter up to {max_channels} channel IDs, comma-separated: ").split(',')
        return [id.strip() for id in channel_ids if id.strip()]

def process_channels_from_csv(csv_file, slack_client):
    """Processes channels from a CSV file based on the specified status.

    Args:
        csv_file: The path to the CSV file containing channel IDs and statuses.
        slack_client: An instance of the Slack WebClient.
    """
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            channel_id = row['channel_id'].strip()
            action = row['channel_status'].strip().lower()
            if action == 'archive':
                archive_channels([channel_id], slack_client)
            elif action == 'unarchive':
                unarchive_channels([channel_id], slack_client)
            else:
                print(f"Invalid action '{action}' for channel {channel_id}. Expected 'archive' or 'unarchive'.")

def main():
    # Prompt for the Slack access token
    token_path = input("Please enter the path to your Slack access token file: ")
    access_token = get_slack_token(token_path)
    slack_client = WebClient(token=access_token)

    # Prompt the user to choose the number of channels to update
    choice = input("Do you want to update one, a few, or many channels? (one/few/many): ").lower()
    channel_ids = []

    if choice in ["one", "few"]:
        # Get the channel IDs from the user
        channel_ids = get_channel_ids_from_user(1 if choice == "one" else 10)
        # Prompt for the action to perform
        action = input("Do you want to archive or unarchive the channels? (archive/unarchive): ").lower()
        if action == "archive":
            archive_channels(channel_ids, slack_client)
        elif action == "unarchive":
            unarchive_channels(channel_ids, slack_client)
        else:
            print("Invalid action. Please enter 'archive' or 'unarchive'.")
    elif choice == "many":
        # Get the CSV file location from the user
        csv_file = input("Enter the CSV file location (channel_id,channel_status): ")
        process_channels_from_csv(csv_file, slack_client)
    else:
        print("Invalid choice. Please enter 'one', 'few', or 'many'.")

if __name__ == "__main__":
    main()
