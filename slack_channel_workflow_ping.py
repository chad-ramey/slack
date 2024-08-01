"""
Script: WIP Slack Ping Channel

Description:
This script is designed to audit Slack channels by sending a message to specified channels.
In the short term, it was used to clean up legacy Slack channels.
In the long term, the script will monitor channel activity and membership to auto-archive or ping the channel to see if it is still needed.

Functions:
- post_message: Sends a message to the specified Slack channels using the Slack API.
- main: The main function that handles user input and calls the appropriate functions to send messages.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. Choose whether to send the message to one, few, or many channels.
   - If "one" is chosen, provide the channel ID.
   - If "few" is chosen, provide the channel IDs separated by commas.
   - If "many" is chosen, provide the path to a CSV file containing the channel IDs.

CSV File Requirements:
- The CSV file should contain a header named 'channel_id' and the channel IDs in the subsequent rows.

Notes:
- Ensure that the Slack token has the necessary permissions to send messages to the channels.
- Handle the Slack token securely and do not expose it in the code.
- Customize the message blocks as needed to fit the organization's requirements.

Author: Chad Ramey
Date: August 1, 2024
"""

import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def post_message(client, channel_ids, message_blocks):
    for channel_id in channel_ids:
        try:
            response = client.chat_postMessage(channel=channel_id, blocks=message_blocks, text="Slack Channel Audit")
            print(f"Message posted successfully in {channel_id}")
        except SlackApiError as e:
            print(f"Error posting to {channel_id}: {e.response['error']}")

def main():
    # User inputs the path to the Slack token file
    token_path = input("Please enter the path to your Slack token file: ")
    with open(token_path, 'r') as token_file:
        slack_token = token_file.read().strip()
    
    client = WebClient(token=slack_token)

    # Define the message blocks
    message_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":broom: Slack Channel Audit: Keep or Archive :broom:",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Please complete the following Slack Workflow to let Collaboration Systems know if this channel is still in use:* :point_right: *<https://slack.com/shortcuts/Ft06USE22XFB/e256ca2560770cdfcac0d1cc73d549ff|Slack Channel Keep or Archive>* :point_left:."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "If this channel is no longer needed, Collaboration Systems will archive it for you or you can archive it by following the instructions listed below. Thank you for your time and support."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "If you have any questions or concerns, please ping...."
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":question: How to Archive a Slack Channel :question:",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": " ",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Step One:* Open the channel you'd like to archive."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Step Two:* Click the channel name in the conversation header."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Step Three:* Click Settings, then Archive channel for everyone."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Step Four:* Click Archive channel to confirm."
            }
        }
    ]

    # Ask the user how many channels to send the message to
    choice = input("Do you want to send the message to one, few, or many channels? (one/few/many): ")
    if choice == "one":
        channel_ids = [input("Enter the channel ID: ")]
    elif choice == "few":
        channel_ids = input("Enter channel IDs separated by commas: ").split(',')
    elif choice == "many":
        filename = input("Enter the CSV filename with channel IDs: ")
        channel_ids = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                channel_ids.append(row['channel_id'])
    else:
        print("Invalid choice. Exiting.")
        return

    # Post the message
    post_message(client, channel_ids, message_blocks)

if __name__ == "__main__":
    main()
