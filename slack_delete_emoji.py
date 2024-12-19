"""
Script: Slack Delete Emoji

Description:
This script deletes Slack custom emojis based on user input. Users can choose to delete one, a few, or many emojis, 
with the option to provide emoji names either through direct input or a CSV file.

CSV File Structure:
- The CSV file should contain headers: emoji

Functions:
- delete_emojis: Deletes the specified emojis.
- read_csv: Reads emoji names from a CSV file and deletes the emojis.
- prompt_for_emojis: Prompts the user for emoji names to delete.

Dependencies:
- requests
- pandas (for CSV reading)

Usage:
1. Run the script.
2. Enter the path to your Slack user token file when prompted.
3. Choose whether to delete one, a few, or many emojis.
4. For 'one' or 'few', enter the emoji names through prompts.
5. For 'many', provide the path to a CSV file containing emoji names.

Notes:
- Ensure that the Slack user token has the necessary permissions to delete emojis.
- Handle the Slack token securely and do not expose it in the code.
- Customize the input prompts and error handling as needed for your organization.

Author: Chad Ramey
Date: December 19, 2024
"""

import os
import requests
import pandas as pd

def get_slack_token(token_path):
    """Reads the Slack user token from a file."""
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def delete_emojis(token, emoji_names):
    """Deletes specified Slack custom emojis using requests."""
    url = "https://slack.com/api/admin.emoji.remove"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {token}'
    }

    for emoji in emoji_names:
        payload = f'token={token}&name={emoji}'
        response = requests.post(url, headers=headers, data=payload)
        if response.ok:
            result = response.json()
            if result.get("ok"):
                print(f"Emoji '{emoji}' deleted successfully.")
            else:
                print(f"Failed to delete emoji '{emoji}': {result.get('error')} - Check if the emoji name is correct.")
        else:
            print(f"HTTP error for emoji '{emoji}': {response.status_code} {response.reason}")

def read_csv(file_path):
    """Reads emoji names from a CSV file."""
    try:
        data = pd.read_csv(file_path)
        if "emoji" not in data.columns:
            print("CSV file must contain a header 'emoji'.")
            return []
        return data["emoji"].dropna().tolist()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def prompt_for_emojis():
    """Prompts user for emoji names to delete."""
    option = input("Do you want to delete one, a few, or many emojis? (one/few/many): ").lower()
    if option == "one":
        emoji_name = input("Enter the emoji name to delete: ").strip()
        return [emoji_name] if emoji_name else []
    elif option == "few":
        emoji_names = input("Enter emoji names separated by commas: ").split(',')
        return [emoji.strip() for emoji in emoji_names if emoji.strip()]
    elif option == "many":
        csv_location = input("Enter the path to the CSV file (emoji): ").strip()
        return read_csv(csv_location)
    else:
        print("Invalid option. Please enter 'one', 'few', or 'many'.")
        return []

def main():
    """Main function to handle user input and delete emojis."""
    token_path = input("Please enter the path to your Slack user token file: ").strip()
    if not os.path.exists(token_path):
        print("Token file does not exist. Please provide a valid path.")
        return

    token = get_slack_token(token_path)

    emoji_names = prompt_for_emojis()
    if emoji_names:
        delete_emojis(token, emoji_names)
    else:
        print("No emojis to delete.")

if __name__ == "__main__":
    main()
