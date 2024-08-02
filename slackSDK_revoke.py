"""
Script: Revoke Slack Token

Description:
This script revokes a specified Slack token. The user is prompted to enter the path to a file containing their 
user token, as well as the token to be revoked. The script then uses the Slack API to revoke the specified token.

Functions:
- get_slack_token: Reads the Slack token from a specified file.
- main: Main function to drive the script based on user input.

Usage:
1. Run the script.
2. Enter the path to your user token file when prompted.
3. Enter the token you wish to revoke when prompted.
4. The script will revoke the specified token and provide feedback on the operation's success.

Notes:
- Ensure that the user token has the necessary permissions to revoke other tokens.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import os
from slack_sdk import WebClient

def get_slack_token(token_path):
    """Reads the Slack token from a specified file.

    Args:
        token_path: The path to the file containing the Slack token.

    Returns:
        The Slack token as a string.
    """
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def main():
    """Main function to drive the script based on user input."""
    user_token_path = input("Please enter the path to your user token file: ")
    user_token = get_slack_token(user_token_path)
    token_to_revoke = input("Enter the token to revoke: ")

    client = WebClient(token=user_token)

    try:
        response = client.auth_revoke(test=True, token=token_to_revoke)
        if response["ok"]:
            print("Token was successfully revoked.")
        else:
            print("Token revocation failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
