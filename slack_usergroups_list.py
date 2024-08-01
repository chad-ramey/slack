"""
Script: Slack Export User Groups

Description:
This script exports Slack user group information to a CSV file. It allows the user to specify 
whether to include users, the count of groups, and disabled user groups in the export. The script 
retrieves the user groups from Slack using the Slack API and writes the data to a CSV file.

Functions:
- ask_yes_no: Helper function to prompt for yes/no input and return a boolean value.
- main: The main function that handles user input, retrieves user groups, and writes them to a CSV file.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Answer the prompts to specify whether to include users, the count of groups, and disabled user groups.
4. The script will export the user group data to a CSV file named 'slack_usergroups.csv'.

CSV File Structure:
- The CSV file will contain the following headers: 
  ["id", "team_id", "name", "description", "handle", "is_usergroup", "is_subteam", "is_external", 
   "date_create", "date_update", "date_delete", "auto_type", "auto_provision", "enterprise_subteam_id", 
   "created_by", "updated_by", "deleted_by", "users", "user_count", "channel_count"]

Notes:
- Ensure that the Slack token has the necessary permissions to retrieve user group information.
- Handle the Slack token securely and do not expose it in the code.
- Customize the team ID as needed for your organization.

Author: Chad Ramey
Date: May 7, 2024
"""

import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Helper function to ask for yes/no input and return a boolean value
def ask_yes_no(question):
    while True:
        response = input(question + " (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please respond with 'y' for yes or 'n' for no.")

def main():
    # Get user input for Slack token
    token_path = input("Please enter the path to your Slack token file: ")
    with open(token_path, 'r') as token_file:
        slack_token = token_file.read().strip()

    # Ask the user if they want to include users, count, and disabled groups
    include_users = ask_yes_no("Do you want to include users?")
    include_count = ask_yes_no("Do you want to include the count of groups?")
    include_disabled = ask_yes_no("Do you want to include disabled user groups?")

    # Initialize Slack WebClient
    client = WebClient(token=slack_token)

    try:
        # Retrieve user group list from Slack, passing user preferences
        response = client.usergroups_list(
            include_users=include_users,
            include_count=include_count,
            include_disabled=include_disabled,
            team_id='T03NUH11G'  # Make sure to adjust or parameterize this if needed
        )

        # Check if the response is successful
        if response["ok"]:
            usergroups = response.get("usergroups", [])
        else:
            raise ValueError(f"Error fetching user groups: {response['error']}")

        # Define CSV file headers
        headers = ["id", "team_id", "name", "description", "handle", "is_usergroup", "is_subteam",
                   "is_external", "date_create", "date_update", "date_delete", "auto_type",
                   "auto_provision", "enterprise_subteam_id", "created_by", "updated_by",
                   "deleted_by", "users", "user_count", "channel_count"]

        # Write to CSV
        with open("slack_usergroups.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            for group in usergroups:
                # Prepare row data (ensure fields not available in every group have default values)
                row = {header: group.get(header, "") for header in headers}
                row['users'] = ",".join(group.get('users', []))
                
                writer.writerow(row)

        print("User group data has been exported to slack_usergroups.csv.")

    except SlackApiError as e:
        print(f"Error fetching data from Slack: {e.response['error']}")
    except ValueError as e:
        print(str(e))

if __name__ == "__main__":
    main()
