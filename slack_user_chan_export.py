"""
Script: Slack Export User's Public and Private Channels to CSV

Description:
This script exports a user's public and private Slack channels to a CSV file. 
The token owner or bot must be a member of the private channels to export them. 
The script handles pagination to ensure all channels are fetched and exported.

Functions:
- export_to_csv: Writes channel data to a CSV file.
- main: The main function to fetch and export channel data.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter the user ID whose channels you want to export.
4. Enter the team ID (workspace ID) if needed.

CSV File Structure:
- The CSV file will contain the following headers: 
  ['id', 'name', 'is_private', 'created', 'is_archived', 'num_members']

Notes:
- Ensure that the Slack token has the necessary permissions to access the user's channels.
- The token owner or bot must be in the private channels that the user is in to export them.
- Add other workspace (team) IDs if needed.

Author: Chad Ramey
Date: April 30, 2024
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import csv

def export_to_csv(channels, fields, filename):
    """Writes channel data to a CSV file.

    Args:
        channels: A list of channel objects.
        fields: A list of field names to include in the CSV.
        filename: The name of the CSV file to create.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for channel in channels:
            writer.writerow({field: channel.get(field, '') for field in fields})

def main():
    """Main function to fetch and export channel data."""
    token_path = input("Please enter the path to your Slack token file: ")
    with open(token_path, 'r') as token_file:
        token = token_file.read().strip()

    user_id = input("Please enter the user ID: ")
    team_id = input("Please enter the team ID (T03NUH11G): ")

    client = WebClient(token=token)

    try:
        # Fetch both public and private channels (the user must be a member of private channels)
        response = client.users_conversations(
            types="public_channel,private_channel",
            exclude_archived=True,
            user=user_id,
            team_id=team_id 
        )

        channels = response['channels']
        fields = ['id', 'name', 'is_private', 'created', 'is_archived', 'num_members']

        # Pagination: check if there's more data to fetch
        while response['response_metadata']['next_cursor']:
            cursor = response['response_metadata']['next_cursor']
            response = client.users_conversations(
                types="public_channel,private_channel",
                exclude_archived=True,
                user=user_id,
                team_id=team_id,
                cursor=cursor
            )
            channels += response['channels']

        # Export data to CSV
        export_to_csv(channels, fields, 'slack_channels.csv')
        print("Data exported to slack_channels.csv")

    except SlackApiError as e:
        print(f"Error: {e.response['error']}")  # Improved error message handling

if __name__ == "__main__":
    main()
