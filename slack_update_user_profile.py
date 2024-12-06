"""
Script: Slack Update User Profile for Out of Office/Vacation with Do Not Disturb (DND) Mode

Description:
This script updates a user's Slack profile and activates Do Not Disturb (DND) mode. It can set
display names, status text, status emoji, and status expiration for the user associated with
the provided Slack token or another user, depending on the token's permissions.

Important Notes:
- The ability to update another user's profile and snooze their notifications depends on the
  permissions associated with the provided Slack token.
- Admin-level tokens or tokens with elevated permissions may allow modifying profiles and
  statuses for other users.
- This behavior may vary based on the workspace or token configuration (e.g., Enterprise Grid
  admin tokens).

Required Scopes:
- `users.profile:write` to update user profile details (e.g., display name, status).
- `dnd:write` to manage Do Not Disturb (DND) settings.

Use Cases:
- Admins can set Out of Office statuses for users in their workspace.
- Users can update their own statuses and snooze notifications.

Limitations:
- If the token lacks the required permissions, the script will only update the profile of the
  authenticated user associated with the token.
- Ensure tokens are handled securely and not exposed publicly.

Author: Chad Ramey
Date: August 2, 2024
Last Updated: December 6, 2024 (Reflects capability to update another user's profile and status)
"""


import requests

def get_slack_token(token_path):
    """Reads the Slack token from a specified file.

    Args:
        token_path: The path to the file containing the Slack token.

    Returns:
        The Slack token as a string.
    """
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def set_profile(access_token, user_id, display_name, status_text, status_emoji, status_expiration):
    """Updates the user's profile with the provided information.

    Args:
        access_token: The Slack access token.
        user_id: The ID of the user whose profile needs to be updated.
        display_name: The new display name.
        status_text: The new status text.
        status_emoji: The new status emoji.
        status_expiration: The expiration time for the status in Unix format.
    """
    url = "https://slack.com/api/users.profile.set"
    
    payload = {
        'profile': {
            'display_name': display_name,
            'status_text': status_text,
            'status_emoji': status_emoji,
            'status_expiration': int(status_expiration)
        },
        'user': user_id
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    if response.ok and data.get('ok'):
        print("Profile status successfully updated.")
    else:
        print("Failed to update profile status.")
        if data.get('error'):
            print("Error message:", data['error'])

def set_snooze(access_token, snooze_minutes):
    """Sets the user's Do Not Disturb (DND) mode for the specified duration.

    Args:
        access_token: The Slack access token.
        snooze_minutes: The number of minutes to snooze notifications.
    """
    url = "https://slack.com/api/dnd.setSnooze"
    
    payload = {
        'num_minutes': snooze_minutes
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    if response.ok and data.get('ok'):
        print(f"Notifications snoozed for {snooze_minutes} minutes.")
    else:
        print("Failed to snooze notifications.")
        if data.get('error'):
            print("Error message:", data['error'])

# Prompt the user for input
token_path = input("Please enter the path to your Slack access token file: ")
access_token = get_slack_token(token_path)
user_id = input("Enter user ID: ")
display_name = input("Enter display name: ")
status_text = input("Enter status text: ")
status_emoji = input("Enter status emoji: ")
status_expiration = input("Enter status expiration (Unix Time - 0 for indefinite): ")
snooze_duration = input("Enter snooze duration in minutes (e.g., 1440 for 24 hours): ")

# Update the user's profile
set_profile(access_token, user_id, display_name, status_text, status_emoji, status_expiration)

# Set the snooze (Do Not Disturb) for the user
set_snooze(access_token, int(snooze_duration))
