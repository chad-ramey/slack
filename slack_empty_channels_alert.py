"""
Script: Slack Empty Channels Alert

Description:
This script identifies Slack channels within a specified team that are empty (i.e., have no members) and posts an alert to a designated Slack channel. The script handles rate limits by implementing exponential backoff and retries. 

Functions:
- fetch_channels: Retrieves a list of Slack channels from the Slack API, handling pagination with cursors.
- post_to_slack: Posts a message to a specified Slack channel.
- main: Main function to execute the script. It fetches channels, identifies empty ones, and posts an alert if any empty channels are found.

Usage:
1. Replace placeholder values for `SLACK_TOKEN`, `TEAM_ID`, and `ALERT_CHANNEL` with actual values.
2. Run the script.
3. The script will continuously fetch channels, identify empty ones, and send a notification to the specified Slack channel.

Notes:
- Ensure the Slack token has the necessary permissions to access channel information and post messages.
- The script handles rate limiting by retrying with exponential backoff, capping the delay at 10 minutes.
- The `fetch_channels` function uses pagination to handle large numbers of channels.

Author: Chad Ramey
Date: August 14, 2024
"""

import os
import time
import requests

# Replace with your actual Slack token, team ID, and alert channel ID
SLACK_TOKEN = ''  # Slack token (ensure it has the right permissions)
TEAM_ID = ''  # Your Slack team ID
ALERT_CHANNEL = ''  # Channel ID where alerts should be posted

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

def post_to_slack(message):
    """
    Posts a message to a specified Slack channel.

    Args:
        message (str): The message to post to Slack.

    Returns:
        dict: The response JSON data from Slack API.
    """
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": ALERT_CHANNEL,
        "text": message
    }
    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    if not data.get('ok'):
        print(f"Error posting to Slack: {data.get('error')}")
    return data

def main():
    """
    Main function to execute the script. It fetches channels, identifies empty ones,
    and posts an alert if any empty channels are found.
    """
    cursor = None
    empty_channels = []
    retry_count = 0
    max_retries = 10  # Maximum number of retries for rate limits
    initial_delay = 60  # Initial delay before retrying

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
            break

        retry_count = 0  # Reset retry count after a successful request
        channels = response.get('channels', [])
        for channel in channels:
            if channel.get('num_members') == 0:
                empty_channels.append(f"Channel: {channel['name']} (ID: {channel['id']})")

        cursor = response.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            break

    if empty_channels:
        message = "Empty Slack Channels:\n" + "\n".join(empty_channels)
        post_to_slack(message)

if __name__ == "__main__":
    main()
