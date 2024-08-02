"""
Script: Slack Allowlist Management

Description:
This script allows users to view, add, or remove a group from a Slack channel's allowlist. 
It interacts with the Slack API to perform these actions based on user input.

Functions:
- main: The main function that handles user input and performs the selected action.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Choose an action:
   - 1: View the Restrict Access List Group for a channel.
   - 2: Add a group to a channel's restrict access list.
   - 3: Remove a group from a channel's restrict access list.
4. Enter the required IDs (team ID, channel ID, and group ID as needed) based on the chosen action.

Notes:
- Ensure that the Slack token has the necessary permissions to manage channel allowlists.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def main():
    """Main function to handle user input and manage Slack channel allowlists."""
    print("Select an action:")
    print("1. View Restrict Access List Group")
    print("2. Restrict Access Add Group")
    print("3. Restrict Access Remove Group")
    action = input("Enter your choice (1/2/3): ")

    # Prompt for Slack API token
    token_path = input("Please enter the path to your Slack API token file: ")
    token = get_slack_token(token_path)
    client = WebClient(token=token)

    channel_id = None
    group_id = None
    team_id = input("Enter team ID: ")

    if action in ["2", "3"]:  # For add or remove actions, we need the group_id
        group_id = input("Enter group ID: ")
        channel_id = input("Enter channel ID: ")
    elif action == "1":  # For listing, we don't need the group_id
        channel_id = input("Enter channel ID: ")

    try:
        if action == "1":  # View Restrict Access List Group
            response = client.admin_conversations_restrictAccess_listGroups(
                channel_id=channel_id,
                team_id=team_id
            )
        elif action == "2":  # Restrict Access Add Group
            response = client.admin_conversations_restrictAccess_addGroup(
                channel_id=channel_id,
                team_id=team_id,
                group_id=group_id
            )
        elif action == "3":  # Restrict Access Remove Group
            response = client.admin_conversations_restrictAccess_removeGroup(
                channel_id=channel_id,
                team_id=team_id,
                group_id=group_id
            )
        else:
            raise ValueError("Invalid action selected.")

        print(response.data)
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")

if __name__ == "__main__":
    main()
