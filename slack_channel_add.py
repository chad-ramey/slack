# Slack Channel Add
# Public + Private + Both | One, Few, Many (csv)
# Channel should have a minimum of one member (Owner or User)
# CSV Header: channel_name,channel_type,email

import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Get user inputs
TOKEN = input("Enter Slack API token: ")
WORKSPACE_ID = input("Enter Workspace ID: ")

# Initialize the Slack client
client = WebClient(token=TOKEN)

# Function to create a Slack channel
def create_channel(channel_name, is_private):
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

# Function to get user ID by email
def get_user_id(email):
    try:
        response = client.users_lookupByEmail(email=email)
        return response.data["user"]["id"]
    except SlackApiError as e:
        print(f"Error looking up user: {e.response['error']}")
        return None

# Function to remove token owner from a channel
def remove_user_from_channel(channel_id):
    try:
        response = client.conversations_leave(channel=channel_id)
        if response["ok"]:
            print("Slack owner service account removed from the channel.")
    except SlackApiError as e:
        print(f"Error removing user from channel: {e.response['error']}")

def invite_user_to_channel(user_id, channel_id, channel_name, email):
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
    process_channels(channels, "keep") # Assuming default behavior is to keep the owner in the channel
