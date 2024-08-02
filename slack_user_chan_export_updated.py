"""
Script: Slack Export User's Public and Private Channels to CSV

Description:
This script exports public and private Slack channels that a user is a member of to a CSV file.
It supports exporting data for one user, multiple users, or users specified in a CSV file.
The exported data includes the user's email address and channel information.

CSV File Structure:
- The CSV file for input should contain headers: user_id

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the team ID (workspace ID) if needed.
4. Choose the mode of operation: 
   - 1: Export data for a single user.
   - 2: Export data for multiple users (comma-separated user IDs).
   - 3: Export data for users listed in a CSV file.
5. The script will export the channel data to a CSV file named 'slack_channels.csv'.

Notes:
- Ensure that the Slack token has the necessary permissions to access user and channel information.
- Handle the Slack token securely and do not expose it in the code.
- Customize the output file name as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import csv

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def export_to_csv(channels, fields, filename):
    """Writes channel data to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for channel in channels:
            writer.writerow({field: channel.get(field, '') for field in fields})

def fetch_user_email(client, user_id):
    """Fetches the email address of a given user with backoff."""
    retries = 0
    while retries < 5:  # Maximum of 5 retries
        try:
            user_info = client.users_info(user=user_id)
            return user_info['user']['profile'].get('email', '')
        except SlackApiError as e:
            if e.response['error'] == 'ratelimited':
                delay = int(e.response.headers.get('Retry-After', 60))  # Use Retry-After header or default to 60 seconds
                print(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
                retries += 1
            else:
                print(f"Error fetching user email: {e.response['error']}")
                return 'email_not_found'
    return 'email_not_found'

def fetch_channels(client, user_id, team_id):
    """Fetches channel information for a given user and includes the user's email."""
    email = fetch_user_email(client, user_id)
    retries = 0
    while retries < 5:  # Maximum of 5 retries
        try:
            response = client.users_conversations(
                types="public_channel,private_channel",
                exclude_archived=True,
                user=user_id,
                team_id=team_id
            )
            channels = response['channels']

            # Include email in each channel's data
            for channel in channels:
                channel['user_email'] = email

            # Handle pagination
            while response['response_metadata']['next_cursor']:
                cursor = response['response_metadata']['next_cursor']
                response = client.users_conversations(
                    types="public_channel,private_channel",
                    exclude_archived=True,
                    user=user_id,
                    team_id=team_id,
                    cursor=cursor
                )
                for channel in response['channels']:
                    channel['user_email'] = email
                channels += response['channels']

            return channels
        except SlackApiError as e:
            if e.response['error'] == 'ratelimited':
                delay = int(e.response.headers.get('Retry-After', 60))  # Use Retry-After header or default to 60 seconds
                print(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
                retries += 1
            else:
                print(f"Error: {e.response['error']}")
                return None
    return None

def main():
    """Main function to fetch and export channel data."""
    token_path = input("Please enter the path to your Slack token file: ")
    token = get_slack_token(token_path)
    team_id = input("Please enter the team ID (default T03NUH11G): ")
    team_id = team_id or 'T03NUH11G'

    mode = input("Select mode (1: single user, 2: multiple users, 3: CSV file): ")

    client = WebClient(token=token)
    all_channels = []
    fields = ['id', 'name', 'is_private', 'created', 'is_archived', 'num_members', 'user_email']

    if mode == '1':
        user_id = input("Enter the user ID: ")
        channels = fetch_channels(client, user_id, team_id)
        if channels:
            all_channels.extend(channels)
    elif mode == '2':
        user_ids = input("Enter user IDs separated by commas: ").split(',')
        for user_id in user_ids:
            channels = fetch_channels(client, user_id.strip(), team_id)
            if channels:
                all_channels.extend(channels)
    elif mode == '3':
        filename = input("Enter the CSV filename containing user IDs: ")
        with open(filename, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                channels = fetch_channels(client, row['user_id'], team_id)
                if channels:
                    all_channels.extend(channels)

    if all_channels:
        export_to_csv(all_channels, fields, 'slack_channels.csv')
        print("Data exported to slack_channels.csv")
    else:
        print("No data to export.")

if __name__ == "__main__":
    main()
