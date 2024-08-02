"""
Script: Slack Export Users to CSV

Description:
This script exports users from specified Slack workspaces to a CSV file. The user is prompted to enter 
the number of workspaces and the corresponding team IDs. The script then retrieves all users from the 
specified workspaces and writes the user details to a CSV file.

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- get_all_users: Retrieves all users from a specified Slack workspace.
- export_to_csv: Writes user details to a CSV file.
- main: Main function to drive the script based on user input.

Usage:
1. Run the script.
2. Enter the number of workspaces when prompted.
3. Enter the path to your Slack token file when prompted.
4. Enter the team IDs for the workspaces when prompted.
5. The script will generate a CSV file with user details for the specified workspaces.

Notes:
- Ensure that the Slack token has the necessary permissions to retrieve user information.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import requests
import csv

def get_slack_token(token_path):
    """Reads the Slack token from a specified file.

    Args:
        token_path: The path to the file containing the Slack token.

    Returns:
        The Slack token as a string.
    """
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def get_all_users(slack_token, team_id):
    """Retrieves all users from a specified Slack workspace.

    Args:
        slack_token: The Slack API token.
        team_id: The ID of the Slack team (workspace).

    Returns:
        A list of users in the specified Slack workspace.
    """
    url = f"https://slack.com/api/admin.users.list?team_id={team_id}&limit=100"
    headers = {
        'Authorization': f'Bearer {slack_token}'
    }

    all_users = []

    while True:
        response = requests.get(url, headers=headers)
        data = response.json()

        if not data['ok']:
            print("Error:", data.get('error', 'Unknown error'))
            return []

        all_users.extend(data['users'])

        if 'response_metadata' in data and 'next_cursor' in data['response_metadata']:
            next_cursor = data['response_metadata']['next_cursor']
            if next_cursor:
                url = f"https://slack.com/api/admin.users.list?team_id={team_id}&limit=100&cursor={next_cursor}"
            else:
                break
        else:
            break

    return all_users

def export_to_csv(users, filename):
    """Writes user details to a CSV file.

    Args:
        users: A list of users.
        filename: The name of the CSV file to create.
    """
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['id', 'email', 'is_admin', 'is_owner', 'is_primary_owner', 'is_restricted', 'is_ultra_restricted', 'is_bot']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow({
                'id': user['id'],
                'email': user['email'],
                'is_admin': user['is_admin'],
                'is_owner': user['is_owner'],
                'is_primary_owner': user['is_primary_owner'],
                'is_restricted': user['is_restricted'],
                'is_ultra_restricted': user['is_ultra_restricted'],
                'is_bot': user['is_bot']
            })

def main():
    """Main function to drive the script based on user input."""
    num_workspaces = int(input("Enter the number of workspaces: "))
    token_path = input("Enter the path to your Slack token file: ")
    slack_token = get_slack_token(token_path)

    all_users = []

    for i in range(num_workspaces):
        team_id = input(f"Enter the team ID for workspace {i + 1}: ")
        workspace_users = get_all_users(slack_token, team_id)
        all_users.extend(workspace_users)

    if all_users:
        filename = "all_slack_users.csv"
        export_to_csv(all_users, filename)
        print(f"All users exported to {filename}")

if __name__ == "__main__":
    main()
