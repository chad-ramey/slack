"""
Script: Slack Delete Channel

Description:
This script deletes Slack channels based on user input. Users can choose to delete one, a few, or many channels, 
with the option to provide channel IDs either through direct input or a CSV file.

CSV File Structure:
- The CSV file should contain headers: channel_id

Functions:
- delete_channels: Deletes the specified channels.
- read_csv: Reads channel IDs from a CSV file and deletes the channels.
- prompt_for_channels: Prompts the user for channel IDs to delete.

Usage:
1. Run the script.
2. Enter the path to your Slack app token file when prompted.
3. Choose whether to delete one, a few, or many channels.
4. For 'one' or 'few', enter the channel IDs through prompts.
5. For 'many', provide the path to a CSV file containing channel IDs.

Notes:
- Ensure that the Slack token has the necessary permissions to delete channels.
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

# Prompt the user for the Slack app token
token_path = input("Please enter the path to your Slack app token file: ")
token = get_slack_token(token_path)
client = WebClient(token=token)

def delete_channels(channel_ids):
    """Deletes the specified channels.

    Args:
        channel_ids: A list of channel IDs to be deleted.

    Returns:
        A list of successfully deleted channel IDs.
    """
    deleted_channel_names = []
    for channel_id in channel_ids:
        retry = True
        while retry:
            try:
                response = client.admin_conversations_delete(channel_id=channel_id)
                if response['ok']:
                    deleted_channel_names.append(channel_id)
                    print(f"Channel {channel_id} deleted successfully.")
                else:
                    print(f"Error deleting channel {channel_id}: {response['error']}")
                retry = False
            except SlackApiError as e:
                if e.response["error"] == "channel_not_found":
                    print(f"Channel {channel_id} does not exist or is not accessible.")
                    retry = False
                elif e.response.status_code == 429:  # Rate-limited error
                    print(f"Rate-limited. Retrying after {e.response.headers['Retry-After']} seconds...")
                    retry_after = int(e.response.headers['Retry-After'])
                    time.sleep(retry_after)
                else:
                    print(f"An error occurred while deleting channel {channel_id}: {e.response['error']}")
                    retry = False
    return deleted_channel_names

def read_csv(filename):
    """Reads channel IDs from a CSV file and deletes the channels.

    Args:
        filename: The path to the CSV file.
    """
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        channel_ids = [row['channel_id'] for row in reader]
        deleted_channels = delete_channels(channel_ids)
        if deleted_channels:
            print("Deleted channels:", ", ".join(deleted_channels))
        else:
            print("No channels were deleted.")

def prompt_for_channels():
    """Prompts the user for channel IDs to delete."""
    option = input("Do you want to delete one, a few, or many channels? (one/few/many): ").lower()
    if option == "one":
        channel_id = input("Enter the channel ID: ")
        delete_channels([channel_id])
    elif option == "few":
        channel_ids = input("Enter up to 10 channel IDs, separated by commas (e.g., C066EPR6J7M,C0673S8EF16): ").split(',')
        delete_channels(channel_ids)
    elif option == "many":
        csv_location = input("Enter the path to the CSV file (channel_id): ")
        read_csv(csv_location)
    else:
        print("Invalid option. Please enter 'one', 'few', or 'many'.")

prompt_for_channels()
