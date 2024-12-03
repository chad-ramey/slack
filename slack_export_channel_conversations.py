"""
Script: Slack Export Channel Conversations

Description:
This script exports all messages from a specified Slack channel to a JSON file. 
Users will be prompted for the location of their Slack token file and the channel ID 
they wish to export messages from. The exported data will include messages and 
metadata for the specified channel.

Usage:
1. Install the Slack SDK using 'pip install slack_sdk'.
2. Run the script.
3. Enter the path to your Slack token file when prompted.
4. Provide the channel ID for the channel whose conversations you want to export.
5. The script will save the exported messages to a JSON file in the current directory.

Notes:
- Ensure the Slack token has the necessary permissions to fetch channel history 
  (e.g., `channels:history` for public channels, `groups:history` for private channels).
- For private channels, ensure the user or app associated with the token is a member of the channel.

Author: Chad Ramey
Date: December 3, 2024
"""

import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    """Reads the Slack token from a specified file."""
    try:
        with open(token_path, 'r') as token_file:
            return token_file.read().strip()
    except FileNotFoundError:
        print(f"Error: File not found at {token_path}")
        exit(1)
    except Exception as e:
        print(f"An error occurred while reading the token file: {e}")
        exit(1)

def fetch_channel_messages(client, channel_id):
    """Fetches all messages from a specified Slack channel."""
    try:
        messages = []
        has_more = True
        next_cursor = None

        while has_more:
            # Fetch messages using conversations.history
            response = client.conversations_history(
                channel=channel_id,
                cursor=next_cursor,
                limit=200
            )
            messages.extend(response["messages"])
            has_more = response.get("has_more", False)
            next_cursor = response.get("response_metadata", {}).get("next_cursor")

        return messages

    except SlackApiError as e:
        print(f"Error fetching messages: {e.response['error']}")
        exit(1)

def save_messages_to_file(messages, filename="channel_messages.json"):
    """Saves messages to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(messages, file, indent=4, ensure_ascii=False)
        print(f"Messages saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
        exit(1)

def main():
    """Main function to prompt the user and export Slack messages."""
    print("Welcome to the Slack Channel Export Script!")

    # Prompt the user for the Slack token location
    token_path = input("Please enter the path to your Slack token file: ")
    token = get_slack_token(token_path)

    # Prompt the user for the channel ID
    channel_id = input("Please enter the Slack Channel ID to export messages from: ")

    # Initialize Slack client
    client = WebClient(token=token)

    print("Fetching messages...")
    messages = fetch_channel_messages(client, channel_id)
    print(f"Fetched {len(messages)} messages.")

    # Save messages to a JSON file
    save_messages_to_file(messages)

if __name__ == "__main__":
    main()
