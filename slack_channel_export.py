"""
Slack Channel Export Script
---------------------------

This script exports Slack channel information to a CSV file using the `slack_sdk` library. It fetches channels in batches, including both public and private channels, and continues until all channels are retrieved. The script prompts the user for the path to a text file containing their Slack user token and the Slack team ID.

Features:
- Fetches channel details using the Slack API.
- Supports pagination to retrieve all channels.
- Exports channel details to a CSV file, including:
  - Team ID
  - Channel ID
  - Channel Name
  - Creation Date
  - Archive Status
  - Number of Members
  - Privacy Status (Public/Private)
  - General Status
  - External Sharing Status
  - Organization Sharing Status
  - Channel Creator

Requirements:
- slack_sdk: Install via `pip install slack_sdk`

Usage:
1. Ensure you have a Slack user token saved in a text file.
2. Run the script and provide the path to the token file and your Slack team ID when prompted.
3. The script will export the channel information to a file named `slack_channels.csv`.

Note:
- The script includes error handling to manage issues such as missing files or API errors.
- Ensure that the Slack user token has the necessary permissions to access channel information.

Author: Chad Ramey
Date: August 1, 2024
"""

import csv
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Function to read the Slack token from a file
def read_token_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            token = file.read().strip()
            return token
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading token from file: {e}")
        return None

# Prompt for the path to the Slack token file
token_file_path = input("Please enter the path to your Slack user token file: ")
token = read_token_from_file(token_file_path)

if not token:
    print("Failed to retrieve Slack user token. Exiting script.")
    exit(1)

# Prompt for the team ID
team_id = input("Please enter your Slack team ID: ")

# Initialize a Web API client with the user token
client = WebClient(token=token)

# File path for the CSV output
csv_file_path = "slack_channels.csv"

# Open the CSV file for writing
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write the header row
    writer.writerow(["Team ID", "Channel ID", "Name", "Created", "Is Archived", "Num Members", "Is Private", "Is General", "Is Ext Shared", "Is Org Shared", "Creator"])

    next_cursor = None
    while True:
        try:
            # Fetch the list of channels, including both public and private channels
            response = client.conversations_list(
                team_id=team_id,
                types="public_channel,private_channel",
                limit=1000,
                cursor=next_cursor
            )
            channels = response.get("channels", [])

            # Debugging: Print the response metadata and channels count
            print(f"Response Metadata: {response.get('response_metadata')}")
            print(f"Fetched {len(channels)} channels")

            # Write channel data to the CSV file
            for channel in channels:
                writer.writerow([
                    team_id,
                    channel.get("id"),
                    channel.get("name"),
                    channel.get("created"),
                    channel.get("is_archived"),
                    channel.get("num_members"),
                    channel.get("is_private"),
                    channel.get("is_general"),
                    channel.get("is_ext_shared"),
                    channel.get("is_org_shared"),
                    channel.get("creator")
                ])

            # Check for the next page
            next_cursor = response["response_metadata"].get("next_cursor")
            if not next_cursor:
                break

        except SlackApiError as e:
            print(f"Error fetching channels: {e.response['error']}")
            print(f"Response: {e.response}")
            break

print(f"Channels exported to {csv_file_path}")
