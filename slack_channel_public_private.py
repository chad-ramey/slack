"""
Script: Slack Convert Channel Private + Public

Description:
This script converts Slack channels from private to public or vice versa based on the channel IDs provided in a CSV file.
No headers are required for the CSV file, and it should contain one channel ID per line.

Functions:
- convert_channels: Converts the specified channels to the desired type (public/private).

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the location of the CSV file containing channel IDs.
4. Specify the desired conversion type (public/private).

Notes:
- Ensure that the Slack token has the necessary permissions to convert channels.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def convert_channels(channel_ids, conversion_type, access_token):
    """Converts the specified channels to the desired type (public/private).

    Args:
        channel_ids: A list of channel IDs to be converted.
        conversion_type: The type to convert the channels to ('public' or 'private').
        access_token: The Slack access token.
    """
    client = WebClient(token=access_token)

    if conversion_type.lower() == "public":
        method = client.admin_conversations_convertToPublic
    elif conversion_type.lower() == "private":
        method = client.admin_conversations_convertToPrivate
    else:
        print("Invalid conversion type. Please enter 'public' or 'private'.")
        return

    for channel_id in channel_ids:
        try:
            response = method(channel_id=channel_id)
            if response['ok']:
                print(f"Channel {channel_id} converted successfully.")
            else:
                print(f"Failed to convert channel {channel_id}.")
                print("Error message:", response.get('error', "Unknown error"))
        except SlackApiError as e:
            print(f"Failed to convert channel {channel_id}.")
            print("Error message:", e.response["error"])

# Ask the user for the token file path
token_path = input("Please enter the path to your Slack token file: ")
access_token = get_slack_token(token_path)

# Ask the user for the CSV file location
csv_file = input("Enter the CSV file location (no headers): ")

# Read channel IDs from CSV
channel_ids = []
with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        channel_ids.extend(row)

# Ask user for conversion type
conversion_type = input("Enter Channel conversion type (public/private): ")

# Call the function to convert the channels
convert_channels(channel_ids, conversion_type, access_token)
