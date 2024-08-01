"""
Script: Slack Disable + Enable User Groups by Group ID

Description:
This script is designed to enable or disable Slack user groups by their group IDs. 
It provides options to process one, a few, or many user groups based on user input.
The script uses the Slack API and handles rate limiting by retrying failed requests.

Functions:
- process_user_groups: Processes the specified user groups by enabling or disabling them.
- main: The main function that handles user input and calls the appropriate functions to process user groups.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Choose whether to 'enable' or 'disable' user groups.
4. Specify whether you have 'one', 'few', or 'many' groups.
   - If 'one' is chosen, provide the group ID.
   - If 'few' is chosen, provide up to 20 group IDs separated by commas.
   - If 'many' is chosen, provide the path to a CSV file containing the group IDs.

CSV File Requirements:
- The CSV file should contain a header named 'group_id' and the group IDs in the subsequent rows.

Notes:
- Ensure that the Slack token has the necessary permissions to enable or disable user groups.
- Handle the Slack token securely and do not expose it in the code.
- Customize the team ID as needed for your organization.

Author: Chad Ramey
Date: August 1, 2024
"""

import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def process_user_groups(client, action, group_ids, team_id):
    api_method = 'usergroups.enable' if action == 'enable' else 'usergroups.disable'
    retry_groups = []
    for group_id in group_ids:
        success = False
        for _ in range(3):  # Retry up to 3 times
            try:
                response = client.api_call(
                    api_method,
                    json={
                        'usergroup': group_id,
                        'team_id': team_id
                    }
                )
                if response['ok']:
                    print(f"{action.capitalize()}d user group {group_id} successfully.")
                    success = True
                    break
                else:
                    print(f"Error: {response['error']} while processing user group {group_id}.")
            except SlackApiError as e:
                if e.response['error'] == 'ratelimited':
                    print(f"Rate limited. Retrying user group {group_id}...")
                    time.sleep(60)  # Wait for 60 seconds before retrying
                else:
                    print(f"Error: {e.response['error']} while processing user group {group_id}.")
                    break
        if not success:
            retry_groups.append(group_id)

    # Retry failed groups after all initial attempts
    if retry_groups:
        print("Retrying failed groups after initial attempts...")
        process_user_groups(client, action, retry_groups, team_id)

def main():
    # Prompt for user input
    token_path = input("Please enter the path to your Slack token file: ")
    with open(token_path, 'r') as token_file:
        slack_token = token_file.read().strip()

    client = WebClient(token=slack_token)
    team_id = "T03NUH11G"  # Constant team ID

    action = input("Do you want to 'enable' or 'disable' user groups? ").strip().lower()
    if action not in ('enable', 'disable'):
        print("Invalid action. Please choose 'enable' or 'disable'.")
        return

    count = input("Do you have 'one', 'few', or 'many' group(s)? ").strip().lower()
    if count == 'one':
        group_id = input("Enter the group ID: ").strip()
        process_user_groups(client, action, [group_id], team_id)
    elif count == 'few':
        group_ids = input("Enter up to 20 group IDs separated by commas: ").strip().split(',')
        process_user_groups(client, action, [g.strip() for g in group_ids[:20]], team_id)
    elif count == 'many':
        csv_path = input("Enter the path to the CSV file containing the group IDs: ").strip()
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if 'group_id' not in reader.fieldnames:
                    print("Error: The CSV file must contain a 'group_id' header.")
                else:
                    group_ids = [row['group_id'] for row in reader]
                    process_user_groups(client, action, group_ids, team_id)
        except FileNotFoundError:
            print("Error: The specified file was not found.")
    else:
        print("Invalid option. Please choose 'one', 'few', or 'many'.")

if __name__ == "__main__":
    main()
