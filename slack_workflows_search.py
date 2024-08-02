"""
Script: Export Slack Workflows to CSV

Description:
This script exports workflows from a Slack workspace to a CSV file using the Slack API. 
It handles pagination to ensure all workflows are fetched and then writes the data to a CSV file.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. The script will export workflows to a CSV file named 'slack_workflows.csv'.

Notes:
- Ensure that the Slack token has the necessary permissions to access workflows.
- Handle the Slack token securely and do not expose it in the code.
- Customize the URL and headers as needed for your specific use case.

Author: Chad Ramey
Date: August 2, 2024
"""

import requests
import csv

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def main():
    # Get user input for Slack token
    token_path = input("Please enter the path to your Slack token file: ")
    token = get_slack_token(token_path)

    # Set up the request headers with your Slack token
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    # The URL for the Slack API method
    url = 'https://slack.com/api/admin.workflows.search'
    # Initialize pagination
    next_cursor = None
    all_workflows = []
    while True:
        # Parameters for the API call, including pagination cursor
        params = {
            'limit': 50,  # Max limit per API documentation
        }
        if next_cursor:
            params['cursor'] = next_cursor
        # Make the API call
        response = requests.get(url, headers=headers, params=params)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # Check if the API call was successful
            if data['ok']:
                workflows = data['workflows']
                all_workflows.extend(workflows)
                # Check for the next cursor under response metadata
                response_metadata = data.get('response_metadata', {})
                next_cursor = response_metadata.get('next_cursor', '').strip()
                # Break the loop if there is no next cursor
                if not next_cursor:
                    break
            else:
                print("API call was not successful. Please check the error:", data['error'])
                break
        else:
            print("Request failed with status code:", response.status_code)
            break
    # Assuming the extraction of all workflows is successful, continue to CSV export
    csv_file = "slack_workflows.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row if workflows exist
        if all_workflows:
            headers = all_workflows[0].keys()  # Assumes all workflows have the same keys
            writer.writerow(headers)
            # Write the workflow data
            for workflow in all_workflows:
                writer.writerow(workflow.values())
    print(f"Successfully exported {len(all_workflows)} workflows to {csv_file}")

if __name__ == "__main__":
    main()
