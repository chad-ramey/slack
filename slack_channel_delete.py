# Slack Delete Channel: one, few, many
# csv header: channel_id

import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Prompt the user for the Slack app token
token = input("Enter your Slack app token: ")
client = WebClient(token=token)

def delete_channels(channel_ids):
    deleted_channel_names = []
    for channel_id in channel_ids:
        retry = True
        while retry:
            try:
                response = client.admin_conversations_delete(channel_id=channel_id)
                if response['ok']:
                    deleted_channel_names.append(channel_id)
                    print(f"Channel {channel_id} deleted successfully.")
                else:
                    print(f"Error deleting channel {channel_id}: {response['error']}")
                retry = False
            except SlackApiError as e:
                if e.response["error"] == "channel_not_found":
                    print(f"Channel {channel_id} does not exist or is not accessible.")
                    retry = False
                elif e.response.status_code == 429:  # Rate-limited error
                    print(f"Rate-limited. Retrying after {e.response.headers['Retry-After']} seconds...")
                    retry_after = int(e.response.headers['Retry-After'])
                    time.sleep(retry_after)
                else:
                    print(f"An error occurred while deleting channel {channel_id}: {e.response['error']}")
                    retry = False
    return deleted_channel_names

def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        channel_ids = [row['channel_id'] for row in reader]
        deleted_channels = delete_channels(channel_ids)
        if deleted_channels:
            print("Deleted channels:", ", ".join(deleted_channels))
        else:
            print("No channels were deleted.")

def prompt_for_channels():
    option = input("Do you want to delete one, a few, or many channels? (one/few/many): ").lower()
    if option == "one":
        channel_id = input("Enter the channel ID: ")
        delete_channels([channel_id])
    elif option == "few":
        channel_ids = input("Enter up to 10 channel IDs, separated by commas (C066EPR6J7M,C0673S8EF16): ").split(',')
        delete_channels(channel_ids)
    elif option == "many":
        csv_location = input("Enter the path to the CSV file (channel_id): ")
        read_csv(csv_location)
    else:
        print("Invalid option. Please enter 'one', 'few', or 'many'.")

prompt_for_channels()
