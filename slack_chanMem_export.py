"""
Script: Slack Export Channel Membership

Description:
This script exports the membership of specified Slack channels, including user IDs, user names, and email addresses. 
It supports exporting data to a single CSV file or multiple CSV files (one per channel). The script handles rate limiting 
and network errors, making it suitable for large channels.

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- safe_api_call: Makes API calls with retry logic for rate limiting and network errors.
- fetch_user_details: Retrieves user details (username and email) for a list of user IDs.
- export_user_data_to_csv: Exports channel membership data to a CSV file.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Enter a comma-separated list of channel IDs or the path to a CSV file containing channel IDs.
4. Choose whether to export data to a single CSV file or multiple CSV files.
5. The script will generate the CSV file(s) with the membership data.

Notes:
- Ensure that the Slack token has the necessary permissions to access user and channel information.
- For private channels, the bot or user must be added to the channel.
- Handle the Slack token securely and do not expose it in the code.
- Be patient with large channels as the script handles rate limiting by retrying API calls.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    """Reads the Slack token from a specified file.

    Args:
        token_path: The path to the file containing the Slack token.

    Returns:
        The Slack token as a string.
    """
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

# Initialize the Slack WebClient
token_path = input("Please enter the path to your Slack token file: ")
slack_token = get_slack_token(token_path)
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
    """Makes API calls with retry logic for rate limiting and network errors.

    Args:
        api_method: The API method to call.
        **params: Parameters to pass to the API method.

    Returns:
        The response from the API call.

    Raises:
        Exception: If the API request fails after maximum retries.
    """
    base_sleep = 1
    max_retries = 10
    while True:
        try:
            return api_method(**params)
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers.get("Retry-After", 60))
                print(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
            else:
                raise
        except Exception as e:
            print(f"Network error occurred: {str(e)}. Retrying in {base_sleep * 2} seconds.")
            time.sleep(base_sleep * 2)
            base_sleep *= 2
        if base_sleep > 512:
            raise Exception("API request failed after maximum retries.")

def fetch_user_details(user_ids):
    """Retrieves user details (username and email) for a list of user IDs.

    Args:
        user_ids: A list of user IDs.

    Returns:
        A dictionary mapping user IDs to their details (username and email).
    """
    user_details = {}
    for user_id in user_ids:
        if user_id not in user_details:
            user_info = safe_api_call(client.users_info, user=user_id)
            user_details[user_id] = {
                'username': user_info['user']['name'],
                'email': user_info['user']['profile'].get('email', 'N/A')
            }
    return user_details

def export_user_data_to_csv(channel_ids, filename):
    """Exports channel membership data to a CSV file.

    Args:
        channel_ids: A list of channel IDs.
        filename: The name of the CSV file to create.
    """
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Channel ID", "User ID", "Username", "Email Address"])
        for channel_id in channel_ids:
            cursor = None
            user_ids = []
            while True:
                response = safe_api_call(client.conversations_members, channel=channel_id.strip(), cursor=cursor)
                user_ids.extend(response['members'])
                cursor = response['response_metadata'].get('next_cursor')
                if not cursor:
                    break
            user_details = fetch_user_details(set(user_ids))
            for user_id in user_ids:
                details = user_details.get(user_id, {'username': 'N/A', 'email': 'N/A'})
                writer.writerow([channel_id, user_id, details['username'], details['email']])
        print(f"All channel memberships exported to {filename}")

if export_option.lower() == "single":
    combined_csv_filename = "combined_membership.csv"
    export_user_data_to_csv(channel_ids, combined_csv_filename)
elif export_option.lower() == "multiple":
    for channel_id in channel_ids:
        individual_filename = f"channel_{channel_id.strip()}_membership.csv"
        export_user_data_to_csv([channel_id], individual_filename)
else:
    print("Invalid export option. Please specify 'single' or 'multiple'.")
