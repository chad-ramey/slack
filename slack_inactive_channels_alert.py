"""
Script: Slack Inactive Channels Alert

Description:
This script identifies Slack channels within a specified team that have had no activity for the past 90 days and generates an alert. Instead of pinging all the inactive channels into a Slack channel, it creates a CSV file containing the channels and uploads it to a designated Slack channel. Additionally, the script formats the last message timestamps into a human-readable date and time.

Features:
- Fetches a list of channels from Slack, including public and private channels.
- Retrieves the timestamp of the last message in each channel.
- Compares the last message timestamp to the current time, identifying channels with no activity for 90 days or more.
- Generates a CSV file listing the inactive channels, including their name, ID, and the last message timestamp.
- Uploads the CSV file to a designated Slack channel.

Functions:
1. fetch_channels: Retrieves a list of Slack channels using the Slack API, handling pagination with cursors.
2. fetch_last_message_timestamp: Fetches the timestamp of the most recent message in a specified channel.
3. convert_timestamp_to_datetime: Converts a Slack timestamp into a human-readable date and time format (YYYY-MM-DD HH:MM:SS).
4. write_to_csv: Writes the list of inactive channels to a CSV file.
5. upload_csv_to_slack: Uploads the generated CSV file to a specified Slack channel.
6. main: Executes the script, orchestrating the process of fetching channels, checking for inactivity, generating the CSV, and uploading it to Slack.

Usage:
1. Store the `SLACK_TOKEN`, `TEAM_ID`, and `ALERT_CHANNEL` as environment variables.
2. Run the script.
3. The script will generate and upload a CSV file containing channels with no activity in the past 90 days to the designated Slack channel.

Prerequisites:
- Ensure the Slack token has the necessary permissions to access channel information (`conversations.list`, `conversations.history`) and upload files (`files:write`).
- The script handles rate limiting by retrying with exponential backoff, capping the delay at 10 minutes.
- This script can be automated using GitHub Actions, with environment variables managed through GitHub Secrets for sensitive data (e.g., `SLACK_TOKEN`).

Author: Chad Ramey
Date: September 10, 2024
"""

import os
import time
import requests
import csv
from datetime import datetime, timedelta

# Fetch values from environment variables
SLACK_TOKEN = os.getenv('SLACK_TOKEN')  # Slack token
TEAM_ID = os.getenv('TEAM_ID')  # Your Slack team ID
ALERT_CHANNEL = os.getenv('ALERT_CHANNEL')  # Channel ID where alerts should be posted
CSV_FILENAME = "inactive_slack_channels.csv"  # Output CSV filename

def fetch_channels(cursor=None):
    """
    Fetches a list of Slack channels from the Slack API.

    Args:
        cursor (str, optional): The cursor for pagination, if available.

    Returns:
        tuple: A tuple containing:
            - data (dict): The response JSON data from Slack API.
            - response.headers (dict): The response headers from the Slack API.
    """
    url = "https://slack.com/api/conversations.list"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }
    params = {
        "exclude_archived": "true",
        "types": "public_channel,private_channel",
        "team_id": TEAM_ID,
        "limit": 100
    }
    if cursor:
        params["cursor"] = cursor

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    if not data.get('ok'):
        print(f"Error fetching channels: {data.get('error')}")
    return data, response.headers

def fetch_last_message_timestamp(channel_id):
    """
    Fetches the timestamp of the most recent message in a channel.

    Args:
        channel_id (str): The ID of the channel.

    Returns:
        str: The timestamp of the most recent message, or None if no messages found.
    """
    url = "https://slack.com/api/conversations.history"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }
    params = {
        "channel": channel_id,
        "limit": 1
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data.get('ok'):
        print(f"Error fetching messages for channel {channel_id}: {data.get('error')}")
        return None

    messages = data.get('messages', [])
    if messages:
        return messages[0].get('ts')
    return None

def convert_timestamp_to_datetime(ts):
    """
    Converts a Slack timestamp to a human-readable datetime format.
    
    Args:
        ts (str): The Slack timestamp.

    Returns:
        str: The converted datetime string.
    """
    if ts:
        return datetime.utcfromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S')
    return None

def write_to_csv(channels):
    """
    Writes the inactive channels to a CSV file.

    Args:
        channels (list): List of dictionaries containing channel details.
    """
    with open(CSV_FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Channel Name', 'Channel ID', 'Last Message Timestamp'])
        for channel in channels:
            writer.writerow([channel['name'], channel['id'], channel['last_message']])

def upload_csv_to_slack():
    """
    Uploads the CSV file to Slack.
    """
    url = "https://slack.com/api/files.upload"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }
    data = {
        "channels": ALERT_CHANNEL,
        "title": "Inactive Slack Channels",
        "initial_comment": "Here are the Slack channels with no activity in the last 90 days.",
    }
    files = {
        'file': (CSV_FILENAME, open(CSV_FILENAME, 'rb'))
    }
    response = requests.post(url, headers=headers, data=data, files=files)
    response_data = response.json()

    if not response_data.get('ok'):
        print(f"Error uploading CSV to Slack: {response_data.get('error')}")
    else:
        print("CSV uploaded successfully to Slack.")

def main():
    """
    Main function to execute the script.
    """
    print("Starting Slack Inactive Channels Alert script...")
    cursor = None
    inactive_channels = []
    retry_count = 0
    max_retries = 10  # Maximum number of retries for rate limits
    initial_delay = 60  # Initial delay before retrying

    # Calculate the timestamp for 90 days ago
    threshold_time = (datetime.now() - timedelta(days=90)).timestamp()

    while True:
        response, headers = fetch_channels(cursor)
        if response.get('error') == 'ratelimited':
            retry_count += 1
            if retry_count > max_retries:
                print("Max retries reached. Exiting.")
                break

            retry_after = int(headers.get('Retry-After', initial_delay))  # Delay before retrying
            retry_delay = min(retry_after * (2 ** (retry_count - 1)), 600)  # Exponential backoff with max delay
            print(f"Rate limited. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            continue

        if not response.get('ok'):
            print("Error fetching channels, exiting...")
            break

        retry_count = 0  # Reset retry count after a successful request
        channels = response.get('channels', [])
        print(f"Fetched {len(channels)} channels.")
        for channel in channels:
            last_message_ts = fetch_last_message_timestamp(channel['id'])
            if last_message_ts and float(last_message_ts) < threshold_time:
                last_message_dt = convert_timestamp_to_datetime(last_message_ts)
                inactive_channels.append({
                    'name': channel['name'],
                    'id': channel['id'],
                    'last_message': last_message_dt
                })

        cursor = response.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            break

    if inactive_channels:
        write_to_csv(inactive_channels)
        upload_csv_to_slack()
        print(f"Generated and uploaded CSV for {len(inactive_channels)} inactive channels.")
    else:
        print("No inactive channels found.")

if __name__ == "__main__":
    main()
