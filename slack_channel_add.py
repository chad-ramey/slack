"""
Script: Slack Channel Add

Description:
This script adds new channels to a Slack workspace. Channels can be public or private, and the user can add 
one, a few, or many channels by providing details either through prompts or a CSV file. Each channel must 
have at least one member (Owner or User).

CSV File Structure:
- The CSV file should contain headers: channel_name, channel_type, email

Functions:
- create_channel: Creates a new Slack channel.
- get_user_id: Retrieves the Slack user ID based on the email.
- remove_user_from_channel: Removes the token owner from a channel.
- invite_user_to_channel: Invites a user to a Slack channel.
- process_channels: Processes the creation and setup of channels based on provided data.

Usage:
1. Run the script.
2. Enter the path to your Slack API token file when prompted.
3. Choose whether to add one, a few, or many channels.
4. For 'one' or 'few', enter the channel names, privacy settings, and user emails through prompts.
5. For 'many', provide the path to a CSV file containing channel names, types, and user emails.

Notes:
- Ensure that the Slack token has the necessary permissions to create channels and invite users.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

# Get user inputs
token_path = input("Please enter the path to your Slack API token file: ")
TOKEN = get_slack_token(token_path)
WORKSPACE_ID = input("Enter Workspace ID: ")

# Initialize the Slack client
client = WebClient(token=TOKEN)

def create_channel(channel_name, is_private):
    """Creates a new Slack channel.

    Args:
        channel_name: The name of the channel to create.
        is_private: Boolean indicating if the channel is private.

    Returns:
        The response data from the Slack API.
    """
    try:
        response = client.conversations_create(
            name=channel_name,
            is_private=is_private,
            team_id=WORKSPACE_ID
        )
        return response.data
    except SlackApiError as e:
        print(f"Error creating channel: {e.response['error']}")
        return None

def get_user_id(email):
    """Retrieves the Slack user ID based on the email.

    Args:
        email: The email address of the user.

    Returns:
        The Slack user ID.
    """
    try:
        response = client.users_lookupByEmail(email=email)
        return response.data["user"]["id"]
    except SlackApiError as e:
        print(f"Error looking up user: {e.response['error']}")
        return None

def remove_user_from_channel(channel_id):
    """Removes the token owner from a Slack channel.

    Args:
        channel_id: The ID of the channel.
    """
    try:
        response = client.conversations_leave(channel=channel_id)
        if response["ok"]:
            print("Slack owner service account removed from the channel.")
    except SlackApiError as e:
        print(f"Error removing user from channel: {e.response['error']}")

def invite_user_to_channel(user_id, channel_id, channel_name, email):
    """Invites a user to a Slack channel.

    Args:
        user_id: The Slack user ID.
        channel_id: The ID of the channel.
        channel_name: The name of the channel.
        email: The email address of the user.
    """
    try:
        response = client.conversations_invite(
            channel=channel_id,
            users=user_id
        )
        if response["ok"]:
            print(f"User with email '{email}' added to the channel '{channel_name}' successfully!")
        else:
            print(f"Failed to add user with email '{email}' to the channel '{channel_name}'. Error: {response['error']}")
    except SlackApiError as e:
        print(f"Failed to invite user: {e.response['error']}")

def process_channels(channels, owner_removal_choice):
    """Processes the creation and setup of channels based on provided data.

    Args:
        channels: A list of tuples containing channel name, type, and email.
        owner_removal_choice: String indicating whether to remove the owner from the channel.
    """
    for channel_info in channels:
        channel_name = channel_info[0]
        is_private = channel_info[1].lower() == "private" if len(channel_info) > 1 else privacy_choice.lower() == "private"
        email = channel_info[-1] if len(channel_info) > 1 else None

        response = create_channel(channel_name, is_private)
        if response and response["ok"]:
            channel_id = response["channel"]["id"]
            print(f"Channel '{channel_name}' (ID: {channel_id}) created as {'private' if is_private else 'public'} successfully!")

            if email:
                user_id = get_user_id(email)
                if user_id:
                    invite_user_to_channel(user_id, channel_id, channel_name, email)
            if owner_removal_choice.lower() == "remove":
                remove_user_from_channel(channel_id)
        else:
            print(f"Failed to create channel '{channel_name}'. Error: {response['error']}" if response else "Failed to create channel due to an unknown error.")

# Prompt user for input type
input_type = input("Do you want to add one, a few, or many channels? (one/few/many): ").lower()

if input_type in ["one", "few"]:
    # Prompt for channel privacy and owner removal choice
    privacy_choice = input("Should all new channels be public or private? (public/private/individual): ")
    owner_removal_choice = input("Do you want to keep or remove the owner from the new channel? (keep/remove): ")

    channels = []
    if input_type == "one":
        channel_name = input("Enter the channel name: ")
        email = input("Enter the user's email (optional): ") if owner_removal_choice.lower() == "keep" else input("Enter the user's email: ")
        channels.append((channel_name, privacy_choice, email))
    elif input_type == "few":
        for i in range(10):
            channel_name = input(f"Enter the name of channel {i+1} (or press enter to stop): ")
            if not channel_name:
                break
            email = input(f"Enter the email for channel {channel_name} (optional): ") if owner_removal_choice.lower() == "keep" else input(f"Enter the email for channel {channel_name}: ")
            channels.append((channel_name, privacy_choice, email))

    process_channels(channels, owner_removal_choice)

elif input_type == "many":
    CSV_FILE = input("Enter CSV file location (channel_name,channel_type,email): ")
    with open(CSV_FILE, "r") as file:
        reader = csv.DictReader(file)
        channels = [(row["channel_name"], row["channel_type"], row["email"]) for row in reader]
    process_channels(channels, "keep")  # Assuming default behavior is to keep the owner in the channel
else:
    print("Invalid choice. Please enter 'one', 'few', or 'many'.")
