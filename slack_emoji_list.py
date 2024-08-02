"""
Script: Slack Export Emojis to CSV

Description:
This script exports custom emojis from a Slack workspace to a CSV file. It retrieves the emojis along with their 
details such as name, URL, date created, and the email of the user who uploaded them. The script handles rate 
limiting and uses a simple backoff strategy to retry API requests.

Functions:
- get_user_email: Retrieves the email address of a user given their user ID, with caching and rate limit handling.
- fetch_all_emojis: Fetches all custom emojis from the Slack workspace.
- save_to_csv: Saves the emoji data to a CSV file.
- main: The main function that coordinates fetching emojis and saving them to a CSV file.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. The script will export the emoji data to a CSV file named 'emojis.csv'.

Notes:
- Ensure that the Slack token has the necessary permissions to access emoji data.
- Handle the Slack token securely and do not expose it in the code.
- Customize the output file name as needed for your organization.

Author: Chad Ramey
Date: April 25, 2024
"""

import csv
import time
from datetime import datetime, timezone
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_user_email(client, user_id, user_cache):
    """Fetches the email address of a user by their user ID, with caching and rate limit handling.

    Args:
        client: The Slack WebClient instance.
        user_id: The ID of the user.
        user_cache: A dictionary for caching user emails.

    Returns:
        The email address of the user or a placeholder if not found.
    """
    if user_id in user_cache:
        return user_cache[user_id]

    # Simple backoff strategy
    backoff = 1
    while True:
        try:
            response = client.users_info(user=user_id)
            if response['ok']:
                user_email = response['user']['profile'].get('email', 'No email found')
                user_cache[user_id] = user_email
                return user_email
            else:
                print("Failed to fetch user email:", response.get('error'))
                return 'No email found'
        except SlackApiError as e:
            if e.response['error'] == 'ratelimited':
                delay = int(e.response.headers.get('Retry-After', backoff))
                print(f"Rate limited. Retrying after {delay} seconds.")
                time.sleep(delay)
                backoff *= 2  # Increase the backoff time
            else:
                print(f"Error fetching user info: {e}")
                return 'No email found'

def fetch_all_emojis(token):
    """Fetches all custom emojis from the Slack workspace.

    Args:
        token: The Slack API token.

    Returns:
        A list of tuples containing emoji details.
    """
    client = WebClient(token=token)
    emojis = []
    user_cache = {}
    next_cursor = None

    while True:
        try:
            response = client.admin_emoji_list(limit=1000, cursor=next_cursor)
            if response['ok']:
                for name, data in response['emoji'].items():
                    date_created = datetime.fromtimestamp(data['date_created'], timezone.utc).strftime('%m/%d/%Y')
                    uploaded_by = data['uploaded_by']
                    email = get_user_email(client, uploaded_by, user_cache)
                    emojis.append((name, data['url'], date_created, uploaded_by, email))
                next_cursor = response['response_metadata'].get('next_cursor')
                if not next_cursor:
                    break
            else:
                print("Failed to fetch emojis:", response.get('error'))
                break
        except SlackApiError as e:
            print(f"Error fetching emojis: {e}")
            break

    return emojis

def save_to_csv(emojis, filename='emojis.csv'):
    """Saves the emoji data to a CSV file.

    Args:
        emojis: A list of tuples containing emoji details.
        filename: The name of the CSV file to create.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'URL', 'Date Created', 'Uploaded By', 'Email'])
        writer.writerows(emojis)
    print(f"Data has been written to {filename}")

def main():
    """Main function to coordinate fetching emojis and saving them to a CSV file."""
    token_path = input("Please enter the path to your Slack token file: ")
    with open(token_path, 'r') as token_file:
        token = token_file.read().strip()

    emojis = fetch_all_emojis(token)
    save_to_csv(emojis)

if __name__ == "__main__":
    main()
