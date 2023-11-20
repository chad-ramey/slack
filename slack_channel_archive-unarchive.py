# Slack Channel Archive + Unarchive
# One, Few, Many | Only Many can mix statuses
# CSV headers channel_id,channel_status

import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def archive_channels(channel_ids, slack_client):
    for channel_id in channel_ids:
        try:
            response = slack_client.admin_conversations_archive(channel_id=channel_id)
            print(f"Channel {channel_id} archived: {response['ok']}")
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers['Retry-After'])
                print(f"Rate-limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"Error: {e.response['error']} - {e.response['detail']}")

def unarchive_channels(channel_ids, slack_client):
    for channel_id in channel_ids:
        try:
            response = slack_client.admin_conversations_unarchive(channel_id=channel_id)
            print(f"Channel {channel_id} unarchived: {response['ok']}")
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers['Retry-After'])
                print(f"Rate-limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"Error: {e.response['error']} - {e.response['detail']}")

def get_channel_ids_from_user(max_channels=10):
    if max_channels == 1:
        return [input("Enter the channel ID: ").strip()]
    else:
        channel_ids = input(f"Enter up to {max_channels} channel IDs, comma-separated: ").split(',')
        return [id.strip() for id in channel_ids if id.strip()]

def process_channels_from_csv(csv_file, slack_client):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            channel_id = row['channel_id'].strip()
            action = row['channel_status'].strip().lower()
            if action == 'archive':
                archive_channels([channel_id], slack_client)
            elif action == 'unarchive':
                unarchive_channels([channel_id], slack_client)
            else:
                print(f"Invalid action '{action}' for channel {channel_id}. Expected 'archive' or 'unarchive'.")

access_token = input("Enter your access token: ")
slack_client = WebClient(token=access_token)

choice = input("Do you want to update one, a few, or many channels? (one/few/many): ").lower()
channel_ids = []

if choice in ["one", "few"]:
    channel_ids = get_channel_ids_from_user(1 if choice == "one" else 10)
    action = input("Do you want to archive or unarchive the channels? (archive/unarchive): ").lower()
    if action == "archive":
        archive_channels(channel_ids, slack_client)
    elif action == "unarchive":
        unarchive_channels(channel_ids, slack_client)
    else:
        print("Invalid action. Please enter 'archive' or 'unarchive'.")
elif choice == "many":
    csv_file = input("Enter the CSV file location (channel_id,channel_status): ")
    process_channels_from_csv(csv_file, slack_client)
else:
    print("Invalid choice. Please enter 'one', 'few', or 'many'.")
