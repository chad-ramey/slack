"""
Script: Slack Export Workflow Integration

Description:
This script exports Slack workflows to a CSV file. It fetches all workflows using the Slack API 
and writes the relevant data to a CSV file, ensuring fields that are lists or dictionaries are 
properly formatted as JSON strings for better readability.

Functions:
- fetch_all_workflows: Retrieves all workflows from the Slack workspace using pagination.
- export_to_csv: Writes the workflow data to a CSV file.

Usage:
1. Run the script.
2. Enter the path to your Slack token file when prompted.
3. The script will export the workflow data to a CSV file named 'workflows_export.csv'.

Notes:
- Ensure that the Slack token has the necessary permissions to access workflow data.
- Handle the Slack token securely and do not expose it in the code.
- Customize the output file name and headers as needed for your organization.

Author: Chad Ramey
Date: August 2, 2024
"""

import csv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json

def get_slack_token(token_path):
    with open(token_path, 'r') as token_file:
        return token_file.read().strip()

def fetch_all_workflows(token):
    """Fetches all workflows from Slack using pagination.

    Args:
        token: The Slack API token.

    Returns:
        A list of workflow objects.
    """
    client = WebClient(token=token)
    workflows = []
    next_cursor = ""

    while True:
        try:
            response = client.admin_workflows_search(
                team_ids=[],  # Ensure this is correctly set as per your requirements
                query="",
                limit=50,  # Corrected to comply with Slack's API limit requirements
                cursor=next_cursor
            )
            workflows.extend(response["workflows"])
            next_cursor = response.get("response_metadata", {}).get("next_cursor", "")
            if not next_cursor:
                break
        except SlackApiError as e:
            print(f"Error fetching workflows: {e}")
            break
    
    return workflows

def export_to_csv(workflows, filename):
    """Writes workflow data to a CSV file.

    Args:
        workflows: A list of workflow objects.
        filename: The name of the CSV file to create.
    """
    headers = [
        "id", "team_id", "workflow_function_id", "callback_id", "title", "description",
        "input_parameters", "steps", "collaborators", "icons", "is_published",
        "is_home_team_only", "last_updated_by", "unpublished_change_count", "app_id",
        "source", "billing_type", "date_updated", "is_billable", "creation_source_type",
        "creation_source_id", "last_published_version_id", "last_published_date",
        "trigger_ids", "is_sales_home_workflow", "is_sales_elevate"
    ]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for workflow in workflows:
            row = [workflow.get(header, "") for header in headers[:-6]]  # Directly get values for most fields
            for header in headers[-6:]:
                if header in workflow:
                    row.append(json.dumps(workflow[header]))  # Convert lists and dicts to JSON strings
                else:
                    row.append("")
            writer.writerow(row)

def main():
    token_path = input("Please enter the path to your Slack token file: ")
    token = get_slack_token(token_path)
    workflows = fetch_all_workflows(token)
    if workflows:
        filename = "workflows_export.csv"
        export_to_csv(workflows, filename)
        print(f"Exported {len(workflows)} workflows to {filename}")
    else:
        print("No workflows found or error fetching workflows.")

if __name__ == "__main__":
    main()
