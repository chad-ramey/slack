"""
Script: Slack Export Channel Memberships

Description:
This script exports user IDs from specified Slack channels to CSV files. It handles rate limits by retrying requests 
with exponential backoff. The user can choose to export the data to a single CSV file or multiple CSV files.

Functions:
- safe_api_call: Makes API calls to Slack, handling rate limits and network errors with retries.
- export_user_ids_to_csv: Exports user IDs from the specified channels to a CSV file.

Usage:
1. Run the script.
2. Enter the path to your Slack OAuth Access Token file when prompted.
3. Enter a comma-separated list of channel IDs or the path to a CSV file containing channel IDs.
4. Choose whether to export the data to a single CSV file or multiple CSV files.

CSV File Requirements:
- If providing a CSV file for input, it should contain channel IDs in the first column.

Notes:
- Ensure that the Slack token has the necessary permissions to retrieve channel memberships.
- Handle the Slack token securely and do not expose it in the code.
- Customize the output file names as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Get user input for Slack token
token_path = input("Please enter the path to your Slack OAuth Access Token file: ")
with open(token_path, 'r') as token_file:
    slack_token = token_file.read().strip()

# Initialize the Slack WebClient
client = WebClient(token=slack_token)

channel_input = input("Enter a comma-separated list of Channel IDs to export membership from or the path to a CSV file: ")
if channel_input.endswith(".csv"):
    with open(channel_input, mode="r") as csv_file:
        reader = csv.reader(csv_file)
        channel_ids = [row[0] for row in reader]
else:
    channel_ids = channel_input.split(",")

export_option = input("Export data to a single CSV file or multiple CSV files? (single/multiple): ")

def safe_api_call(api_method, **params):
    base_sleep = 1
    max_retries = 10
    for i in range(max_retries):
        try:
            return api_method(**params)
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers.get("Retry-After", base_sleep * (2 ** i)))
                print(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
            else:
                raise
        except Exception as e:
            print(f"Network error occurred: {str(e)}. Retrying in {base_sleep * (2 ** i)} seconds.")
            time.sleep(base_sleep * (2 ** i))
    raise Exception("API request failed after maximum retries.")

def export_user_ids_to_csv(channel_ids, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Channel ID", "User ID"])
        for channel_id in channel_ids:
            cursor = None
            while True:
                response = safe_api_call(client.conversations_members, channel=channel_id.strip(), cursor=cursor)
                user_ids = response['members']
                for user_id in user_ids:
                    writer.writerow([channel_id, user_id])
                cursor = response['response_metadata'].get('next_cursor')
                if not cursor:
                    break

if export_option.lower() == "single":
    combined_csv_filename = "combined_membership.csv"
    export_user_ids_to_csv(channel_ids, combined_csv_filename)
    print(f"All channel memberships exported to {combined_csv_filename}")
elif export_option.lower() == "multiple":
    for channel_id in channel_ids:
        individual_filename = f"channel_{channel_id.strip()}_membership.csv"
        export_user_ids_to_csv([channel_id], individual_filename)
        print(f"Membership data for {channel_id} exported to {individual_filename}.")
else:
    print("Invalid export option. Please specify 'single' or 'multiple'.")
