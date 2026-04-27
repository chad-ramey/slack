"""
Slack Channel Manager
=====================
This script allows managing Slack channels with options to add, delete, archive, unarchive, and update visibility.

Prerequisites:
1. Python Packages:
   - Install required packages using pip:
     pip install slack_sdk

2. Environment Variable:
   - Set the environment variable for your Slack user token:
     export SLACK_USER_TOKEN="xoxp-your-user-token"

3. Required Scopes for the Token:
   - channels:manage
   - channels:read
   - channels:write
   - groups:read
   - groups:write
   - admin.conversations:write
   - admin.conversations:read

Features:
- Add single, multiple, or batch channels.
- Delete, archive, or unarchive channels.
- Update channel visibility (public/private).
- Supports batch operations via CSV files.

Usage:
- Run the script:
  python slack_channel_manager.py
- Follow the on-screen prompts for each operation.

CSV Format Guidelines:
1. Add Channel:
   channel_name,channel_visibility
   project_updates,private
   general,public

2. Delete Channel:
   channel_id
   C07EJNJ2CLX

3. Archive/Unarchive Channel:
   channel_id
   C07EJNJ2CLX

4. Update Channel Visibility:
   channel_id,visibility
   C07EJNJ2CLX,private
   C07EJNJ2CMX,public

Author: Chad Ramey
Last Updated: May 9, 2025
"""

import os
import sys
import csv
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_slack_token():
    token = os.getenv("SLACK_USER_TOKEN")
    if not token:
        print("Error: SLACK_USER_TOKEN environment variable not set.")
        sys.exit(1)
    return token

def select_workspace():
    """Prompt for a Slack team ID. Add your workspace IDs to the dict below."""
    print("\nPlease select your workspace:")
    workspaces = {
        "1": "T_WORKSPACE_1 (Workspace One)",
        "2": "T_WORKSPACE_2 (Workspace Two)",
    }
    for key, value in workspaces.items():
        print(f"{key}. {value}")
    choice = input("Select a workspace number (or enter a team ID directly): ")
    if choice in workspaces:
        return workspaces[choice].split()[0]
    return choice.strip() or None

client = WebClient(token=get_slack_token())

def add_channel(name, is_private, workspace_id):
    try:
        response = client.conversations_create(name=name, is_private=is_private, team_id=workspace_id)
        logging.info(f"Channel '{name}' created successfully in workspace '{workspace_id}'.")
    except SlackApiError as e:
        logging.error(f"Error creating channel '{name}': {e.response['error']}")

def add_channels_from_csv(file_path, workspace_id):
    print("\nPlease ensure your CSV file has the following headers: channel_name, channel_visibility")
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                visibility = row['channel_visibility'].lower() == 'private'
                add_channel(row['channel_name'], visibility, workspace_id)
        logging.info("Batch channel addition complete.")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")

def delete_channel(channel_id):
    try:
        client.conversations_archive(channel=channel_id)
        logging.info(f"Channel '{channel_id}' deleted successfully.")
    except SlackApiError as e:
        logging.error(f"Error deleting channel '{channel_id}': {e.response['error']}")

def delete_channels_from_csv(file_path):
    print("\nPlease ensure your CSV file has the following header: channel_id")
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                delete_channel(row['channel_id'])
        logging.info("Batch channel deletion complete.")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")

def archive_channel(channel_id):
    try:
        client.conversations_archive(channel=channel_id)
        logging.info(f"Channel '{channel_id}' archived successfully.")
    except SlackApiError as e:
        logging.error(f"Error archiving channel '{channel_id}': {e.response['error']}")

def archive_channels_from_csv(file_path):
    print("\nPlease ensure your CSV file has the following header: channel_id")
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                archive_channel(row['channel_id'])
        logging.info("Batch channel archiving complete.")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")

def unarchive_channel(channel_id):
    try:
        client.conversations_unarchive(channel=channel_id)
        logging.info(f"Channel '{channel_id}' unarchived successfully.")
    except SlackApiError as e:
        logging.error(f"Error unarchiving channel '{channel_id}': {e.response['error']}")

def unarchive_channels_from_csv(file_path):
    print("\nPlease ensure your CSV file has the following header: channel_id")
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                unarchive_channel(row['channel_id'])
        logging.info("Batch channel unarchiving complete.")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")

def update_channel_visibility(channel_id, make_private):
    try:
        if make_private:
            response = client.admin_conversations_convertToPrivate(channel_id=channel_id)
            logging.info(f"Channel '{channel_id}' converted to private.")
        else:
            response = client.admin_conversations_convertToPublic(channel_id=channel_id)
            logging.info(f"Channel '{channel_id}' converted to public.")
    except SlackApiError as e:
        logging.error(f"Error updating visibility of channel '{channel_id}': {e.response['error']}")

def update_channels_from_csv(file_path):
    print("\nPlease ensure your CSV file has the following headers: channel_id, visibility")
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                make_private = row['visibility'].lower() == 'private'
                update_channel_visibility(row['channel_id'], make_private)
        logging.info("Batch visibility update complete.")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")


def add_channel_menu():
    print("\nAdd Channel")
    print("a. Single")
    print("b. Multiple (prompted input)")
    print("c. Many (from CSV)")
    print("r. Return to main menu")

def delete_channel_menu():
    print("\nDelete Channel")
    print("a. Single")
    print("b. Multiple (prompted input)")
    print("c. Many (from CSV)")
    print("r. Return to main menu")

def archive_channel_menu():
    print("\nArchive Channel")
    print("a. Single")
    print("b. Multiple (prompted input)")
    print("c. Many (from CSV)")
    print("r. Return to main menu")

def unarchive_channel_menu():
    print("\nUnarchive Channel")
    print("a. Single")
    print("b. Multiple (prompted input)")
    print("c. Many (from CSV)")
    print("r. Return to main menu")

def update_visibility_menu():
    print("\nUpdate Channel Visibility")
    print("a. Single")
    print("b. Multiple (prompted input)")
    print("c. Many (from CSV)")
    print("r. Return to main menu")

def main_menu():
    print("\nSlack Channel Manager")
    print("A. Add Channel")
    print("B. Delete Channel")
    print("C. Archive Channel")
    print("D. Unarchive Channel")
    print("E. Update Channel Visibility")
    print("Q. Quit")

def main():
    while True:
        main_menu()
        choice = input("\nSelect an option: ").upper()

        if choice == 'A':
            add_channel_menu()
            sub_choice = input("Select: ").lower()

            if sub_choice == 'a':
                name = input("Enter channel name: ")
                is_private = input("Private? (yes/no): ").lower() == 'yes'
                workspace_id = select_workspace()
                add_channel(name, is_private, workspace_id)

            elif sub_choice == 'b':
                channels = input("Enter channel names (comma-separated): ").split(',')
                is_private = input("Private? (yes/no): ").lower() == 'yes'
                workspace_id = select_workspace()
                for name in channels:
                    add_channel(name.strip(), is_private, workspace_id)

            elif sub_choice == 'c':
                print("\nFor adding multiple channels from a CSV file, use the following format:")
                print("CSV Headers: channel_name, channel_visibility")
                file_path = input("Enter CSV file path: ")
                workspace_id = select_workspace()
                add_channels_from_csv(file_path, workspace_id)

            elif sub_choice == 'r':
                continue

        elif choice == 'B':
            delete_channel_menu()
            sub_choice = input("Select: ").lower()

            if sub_choice == 'a':
                channel_id = input("Enter channel ID to delete: ")
                delete_channel(channel_id)

            elif sub_choice == 'b':
                channel_ids = input("Enter channel IDs (comma-separated): ").split(',')
                for channel_id in channel_ids:
                    delete_channel(channel_id.strip())

            elif sub_choice == 'c':
                print("\nFor deleting multiple channels from a CSV file, use the following format:")
                print("CSV Header: channel_id")
                file_path = input("Enter CSV file path: ")
                delete_channels_from_csv(file_path)

            elif sub_choice == 'r':
                continue

        elif choice == 'C':
            archive_channel_menu()
            sub_choice = input("Select: ").lower()

            if sub_choice == 'a':
                channel_id = input("Enter channel ID to archive: ")
                archive_channel(channel_id)

            elif sub_choice == 'b':
                channel_ids = input("Enter channel IDs (comma-separated): ").split(',')
                for channel_id in channel_ids:
                    archive_channel(channel_id.strip())

            elif sub_choice == 'c':
                print("\nFor archiving multiple channels from a CSV file, use the following format:")
                print("CSV Header: channel_id")
                file_path = input("Enter CSV file path: ")
                archive_channels_from_csv(file_path)

            elif sub_choice == 'r':
                continue

        elif choice == 'D':
            unarchive_channel_menu()
            sub_choice = input("Select: ").lower()

            if sub_choice == 'a':
                channel_id = input("Enter channel ID to unarchive: ")
                unarchive_channel(channel_id)

            elif sub_choice == 'b':
                channel_ids = input("Enter channel IDs (comma-separated): ").split(',')
                for channel_id in channel_ids:
                    unarchive_channel(channel_id.strip())

            elif sub_choice == 'c':
                print("\nFor unarchiving multiple channels from a CSV file, use the following format:")
                print("CSV Header: channel_id")
                file_path = input("Enter CSV file path: ")
                unarchive_channels_from_csv(file_path)

            elif sub_choice == 'r':
                continue

        elif choice == 'E':
            update_visibility_menu()
            sub_choice = input("Select: ").lower()

            if sub_choice == 'a':
                channel_id = input("Enter channel ID: ")
                make_private = input("Make private? (yes/no): ").lower() == 'yes'
                update_channel_visibility(channel_id, make_private)

            elif sub_choice == 'b':
                channel_ids = input("Enter channel IDs (comma-separated): ").split(',')
                make_private = input("Make private? (yes/no): ").lower() == 'yes'
                for channel_id in channel_ids:
                    update_channel_visibility(channel_id.strip(), make_private)

            elif sub_choice == 'c':
                print("\nFor updating visibility of multiple channels from a CSV file, use the following format:")
                print("CSV Headers: channel_id, visibility")
                file_path = input("Enter CSV file path: ")
                update_channels_from_csv(file_path)

            elif sub_choice == 'r':
                continue


        elif choice == 'Q':
            print("Exiting...")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
