"""
Script: Slack Add or Remove Channels to/from Workspaces

Description:
This script adds or removes Slack channels to/from workspaces using the `admin.conversations.setTeams` API method. 
Users can provide data either via a JSON file or manual input. The script updates the teams for each provided channel ID.

CSV File Structure (if applicable):
- Headers: channel_id, current_team_id, target_team_ids

Functions:
- get_input: Prompts for user input.
- update_channels_from_json: Updates channels based on data provided in a JSON file.
- update_channel_teams: Updates the teams for a specified channel.
- main: Main function to drive the script based on user input.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Choose whether to provide data via JSON or manual input.
4. Provide the required data (JSON path or manual input details).
5. The script will update the channels as specified.

Notes:
- Ensure that the Slack token has the necessary permissions to update channel teams.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def get_input(prompt, multiple=False):
    """Prompts for user input and optionally handles multiple comma-separated values.

    Args:
        prompt: The input prompt message.
        multiple: Boolean indicating if multiple values are expected.

    Returns:
        A single value or a list of values based on the `multiple` parameter.
    """
    value = input(prompt)
    if multiple:
        return [item.strip() for item in value.split(',')]
    return value

def update_channels_from_json(client, json_path):
    """Updates channels based on data provided in a JSON file.

    Args:
        client: The Slack WebClient instance.
        json_path: The path to the JSON file containing channel data.
    """
    with open(json_path, 'r') as file:
        data = json.load(file)
        for item in data:
            channel_id = item["channel_id"]
            current_team_id = item.get("current_team_id", None)
            target_team_ids = item["target_team_ids"]
            
            print(f"Updating channel {channel_id} with current_team_id: {current_team_id} and target_team_ids: {target_team_ids}")
            update_channel_teams(client, channel_id, target_team_ids, current_team_id)

def update_channel_teams(client, channel_id, target_team_ids, current_team_id=None):
    """Updates the teams for a specified channel.

    Args:
        client: The Slack WebClient instance.
        channel_id: The ID of the channel to update.
        target_team_ids: The target team IDs to assign the channel to.
        current_team_id: The current team ID of the channel (if applicable).
    """
    try:
        response = client.admin_conversations_setTeams(
            channel_id=channel_id,
            target_team_ids=target_team_ids,
            team_id=current_team_id,
            org_channel=False
        )
        print(f"Response for channel {channel_id}: {response['ok']}")  
    except SlackApiError as e:
        print(f"Error for channel {channel_id}: {e.response['error']}")

def main():
    """Main function to drive the script based on user input."""
    token_path = get_input("Please enter the path to your Slack token file: ")
    token = get_slack_token(token_path)
    client = WebClient(token=token)
    data_source = get_input("Do you want to provide data via JSON? (yes/no): ").strip().lower()

    if data_source == "yes":
        json_path = get_input("Enter the path to the JSON file: ")
        update_channels_from_json(client, json_path)
    else:
        multiple_channels = get_input("Is this for multiple channels? (yes/no): ").strip().lower() == "yes"
        if multiple_channels:
            channel_ids = get_input("Enter the channel IDs (comma-separated): ", multiple=True)
        else:
            channel_ids = [get_input("Enter the channel ID: ")]

        current_team_id = get_input("Enter the current team ID (leave empty if not needed): ")

        if current_team_id:
            additional_team_ids = get_input("Enter the additional target team IDs (comma-separated): ", multiple=True)
            target_team_ids = [current_team_id] + additional_team_ids
        else:
            target_team_ids = get_input("Enter the target team IDs (comma-separated): ", multiple=True)

        for channel_id in channel_ids:
            update_channel_teams(client, channel_id, target_team_ids, current_team_id if current_team_id else None)

if __name__ == "__main__":
    main()
