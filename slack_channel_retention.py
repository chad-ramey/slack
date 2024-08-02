"""
Script: Slack Channel Set + Remove Retention

Description:
This script sets or removes custom retention policies for Slack channels based on data provided in a CSV file. 
The user can choose to either set a custom retention period or reset the retention settings to default for each channel.

CSV File Structure:
- The CSV file should contain headers: channel_id, num_days

Functions:
- Initialize the Slack SDK client with a token.
- Read channel IDs and retention days from a CSV file.
- Set or reset the channel retention based on user input.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the location of the CSV file containing channel IDs and retention days.
4. Choose whether to set or reset the retention settings.

Notes:
- Ensure that the Slack token has the necessary permissions to manage channel retention settings.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 25, 2023
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import csv

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

# Initialize the Slack SDK client
token_path = input("Please enter the path to your Slack token file: ")
token = get_slack_token(token_path)
client = WebClient(token=token)

# Ask the user for the CSV file location
csv_file = input("Enter the CSV file location: ")

# Read channel IDs and retention days from a CSV file
channels_data = []
with open(csv_file, 'r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip the header row
    for row in csv_reader:
        channel_id = row[0]
        retention_days = int(row[1])  # Assuming the retention days are in the second column
        channels_data.append((channel_id, retention_days))

# Ask the user if they want to set or reset the channel retention
action = input("Do you want to set or reset the channel retention? (set/reset): ").lower()

# Process each channel ID and retention days
for channel_data in channels_data:
    channel_id, retention_days = channel_data
    try:
        if action == "set":
            response = client.admin_conversations_setCustomRetention(channel_id=channel_id, duration_days=retention_days)
            print(f"Channel {channel_id} retention settings successfully updated to {retention_days} days")
        elif action == "reset":
            response = client.admin_conversations_removeCustomRetention(channel_id=channel_id)
            print(f"Channel {channel_id} retention settings successfully reset to the default")
    except SlackApiError as e:
        error_message = e.response["error"]
        print(f"Failed to update retention settings for channel {channel_id}: {error_message}")
