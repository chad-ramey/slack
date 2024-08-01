"""
Slack External Teams Disconnection Script
=========================================

Description:
------------
This script is designed to disconnect external teams from a Slack workspace using the Slack API. 
It utilizes the `slack_sdk` library to send API requests to the `team.externalTeams.disconnect` endpoint. 

Key Features:
-------------
1. **User Input for Bot Token**: Prompts the user to input the location of the bot token text file on their computer.
2. **Choice of Disconnection Scope**: 
   - **One**: Disconnect a single external team by providing its team ID.
   - **Few**: Disconnect multiple external teams by providing a comma-separated list of team IDs.
   - **Many**: Disconnect many external teams by providing a CSV file containing team IDs.
3. **Rate Limiting Handling**: 
   - The script respects Slack's API rate limits by checking the `Retry-After` header.
   - It includes a retry mechanism that waits for the specified period before retrying requests if rate-limited.

Usage Instructions:
-------------------
1. Ensure you have a valid bot token saved in a text file.
2. Run the script and provide the necessary inputs as prompted:
   - Path to the bot token file.
   - Scope of disconnection (one, few, or many).
   - Relevant team IDs or CSV file path.
3. The script will log the success or failure of each disconnection attempt, including handling rate limits.

Considerations:
---------------
- **Rate Limits**: This script is subject to Slack's rate limiting policies. If the rate limit is exceeded, the script will wait for the period specified in the `Retry-After` header before retrying.
- **Error Handling**: Basic error handling is implemented for file reading and API requests. Ensure that your bot token and team IDs are correct and that you have the necessary permissions to perform these actions.
- **Security**: Keep your bot token secure and avoid sharing it or exposing it in public repositories.

Requirements:
-------------
- Python 3.x
- `slack_sdk` library: Install using `pip install slack_sdk`
- A valid Slack bot token with the necessary permissions

Disclaimer:
-----------
Use this script responsibly and in accordance with your organization's policies and Slack's terms of service.
"""

import os
import time
import slack_sdk
import csv
import requests

def read_bot_token(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading token file: {e}")
        return None

def disconnect_team(client, team_id):
    try:
        response = client.api_call(
            "team.externalTeams.disconnect",
            params={'target_team': team_id}
        )
        if response['ok']:
            print(f"Successfully disconnected team: {team_id}")
            return True
        elif response['error'] == 'ratelimited':
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds before retrying...")
            time.sleep(retry_after)
            return 'retry'
        else:
            print(f"Failed to disconnect team: {team_id}, error: {response['error']}")
            return False
    except Exception as e:
        if hasattr(e, 'response') and e.response.status_code == 429:
            retry_after = int(e.response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return 'retry'
        else:
            print(f"Error disconnecting team {team_id}: {e}")
            return False

def process_team_ids(client, team_ids):
    for team_id in team_ids:
        result = disconnect_team(client, team_id)
        if result == 'retry':
            # If rate limited, retry the same team_id after waiting
            print(f"Retrying team {team_id} after waiting.")
            disconnect_team(client, team_id)
        elif not result:
            print(f"Failed to disconnect team {team_id}.")

def main():
    token_file = input("Enter the path to your bot token text file: ")
    token = read_bot_token(token_file)

    if not token:
        print("Invalid bot token. Exiting.")
        return

    client = slack_sdk.WebClient(token=token)

    choice = input("Do you want to disconnect one, few, or many teams? (one/few/many): ").strip().lower()

    if choice == "one":
        team_id = input("Enter the external team ID: ").strip()
        process_team_ids(client, [team_id])

    elif choice == "few":
        team_ids = input("Enter the external team IDs, comma separated: ").split(',')
        team_ids = [team_id.strip() for team_id in team_ids]
        process_team_ids(client, team_ids)

    elif choice == "many":
        csv_file = input("Enter the path to the CSV file with team IDs: ").strip()
        try:
            with open(csv_file, mode='r') as file:
                csv_reader = csv.DictReader(file)
                team_ids = [row['team_id'].strip() for row in csv_reader]
                process_team_ids(client, team_ids)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
