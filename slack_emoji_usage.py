"""
Slack Emoji Usage Script
========================

This script aggregates emoji usage in Slack channels, including:
- Emojis used in message text.
- Emojis added as reactions to messages.

The script reads a list of channel IDs (public and private) from an external CSV file 
and generates a report of emoji usage. It includes options to export the results 
to a CSV file and print them to the console.

Features:
---------
1. Supports both public and private channels.
2. Handles Slack API rate limits gracefully by deferring and retrying channels.
3. Exports results to a CSV file for easy analysis.
4. Prompts the user for:
   - The Slack token file path.
   - The channel CSV file path.
   - The workspace (team) ID.

Requirements:
-------------
- A valid Slack user or bot token with the following scopes:
  - `channels:read`: Access public channel metadata.
  - `groups:read`: Access private channel metadata.
  - `channels:history`: Read public channel message history.
  - `groups:history`: Read private channel message history.
  - `reactions:read` (optional): Fetch reactions on messages.

Setup Instructions:
-------------------
1. Create a plain text file containing your Slack token (e.g., `slack_token.txt`).
2. Prepare a CSV file (`channels.csv`) with the following structure:
    - Replace `channel_id` with the IDs of the channels to process.
    - Include both public (`C...`) and private (`G...`) channel IDs as needed.
3. Run the script and follow the prompts.

Output:
-------
- The script prints an emoji usage report to the console.
- The report is also saved to a CSV file named `emoji_usage_report.csv`.

Author: Chad Ramey
Date: December 10, 2024

"""

import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from urllib.error import URLError
from collections import Counter
import re
import os

# Function to get the Slack token from a file
def get_slack_token_from_file():
    token_file = input("Enter the path to your Slack token file: ").strip()
    if not os.path.exists(token_file):
        raise FileNotFoundError(f"Token file not found at: {token_file}")
    with open(token_file, "r") as file:
        token = file.read().strip()
    print("Slack token loaded successfully.")
    return token

# Function to load channel IDs from a CSV file
def load_channel_ids_from_csv():
    csv_file_path = input("Enter the path to your channels CSV file: ").strip()
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_file_path}")
    with open(csv_file_path, mode="r") as file:
        reader = csv.DictReader(file)
        channel_ids = [row["channel_id"] for row in reader]
    print(f"Loaded {len(channel_ids)} channel IDs from CSV.")
    return channel_ids

# Fetch emoji from conversations.history for a given channel
def fetch_emoji_from_messages(client, channel_id, team_id, max_retries=3):
    emoji_pattern = r":[a-zA-Z0-9_+]+:"
    emoji_counter = Counter()
    retries = 0

    while retries < max_retries:
        try:
            has_more = True
            next_cursor = None

            while has_more:
                response = client.conversations_history(
                    channel=channel_id,
                    team_id=team_id,
                    cursor=next_cursor,
                    limit=200
                )

                for message in response.get("messages", []):
                    # Count emojis in the message text
                    text = message.get("text", "")
                    emojis_in_text = re.findall(emoji_pattern, text)
                    for emoji in emojis_in_text:
                        emoji_counter[emoji.strip(":")] += 1

                    # Count emoji reactions
                    reactions = message.get("reactions", [])
                    for reaction in reactions:
                        emoji_name = reaction["name"]
                        emoji_count = reaction["count"]
                        emoji_counter[emoji_name] += emoji_count

                has_more = response.get("has_more", False)
                next_cursor = response.get("response_metadata", {}).get("next_cursor")
            return emoji_counter

        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers.get("Retry-After", 10))
                print(f"Rate limited for channel {channel_id}. Retrying after {retry_after} seconds...")
                return None  # Defer the channel
            else:
                print(f"Slack API error for channel {channel_id}: {e.response['error']}")
                break

        except URLError as e:
            retries += 1
            print(f"SSL error for channel {channel_id}: {e.reason}. Retrying {retries}/{max_retries}...")
            time.sleep(5)

    print(f"Failed to fetch messages for channel {channel_id} after {max_retries} retries.")
    return emoji_counter

# Main function to aggregate emoji usage
def aggregate_emoji_usage(client, channel_ids, team_id):
    total_emoji_usage = Counter()
    deferred_channels = []  # Queue for rate-limited channels

    # Iterate through channels to fetch emoji from messages
    for index, channel_id in enumerate(channel_ids):
        print(f"Processing channel {index + 1}/{len(channel_ids)}: {channel_id}")
        emoji_counts = fetch_emoji_from_messages(client, channel_id, team_id)
        if emoji_counts is None:
            deferred_channels.append(channel_id)  # Defer rate-limited channels
        else:
            total_emoji_usage.update(emoji_counts)
        time.sleep(2)

    # Reprocess deferred channels
    print(f"Reprocessing {len(deferred_channels)} deferred channels...")
    for channel_id in deferred_channels:
        print(f"Processing deferred channel: {channel_id}")
        emoji_counts = fetch_emoji_from_messages(client, channel_id, team_id)
        if emoji_counts is not None:
            total_emoji_usage.update(emoji_counts)

    return total_emoji_usage

# Save emoji usage to a CSV file
def save_emoji_usage_to_csv(emoji_usage, output_file="emoji_usage_report.csv"):
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Emoji", "Count"])
        for emoji, count in emoji_usage.most_common():
            writer.writerow([emoji, count])
    print(f"Emoji usage report saved to {output_file}.")

# Run the script and display results
if __name__ == "__main__":
    # Load Slack token and channel IDs
    try:
        slack_token = get_slack_token_from_file()
        channel_ids = load_channel_ids_from_csv()
        team_id = input("Enter your team ID: ").strip()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    # Initialize Slack client
    client = WebClient(token=slack_token)

    # Aggregate emoji usage
    emoji_usage = aggregate_emoji_usage(client, channel_ids, team_id)

    # Display and save results
    print("Emoji Usage Report:")
    for emoji, count in emoji_usage.most_common():
        print(f"{emoji}: {count} uses")
    save_emoji_usage_to_csv(emoji_usage)
