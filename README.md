# Slack Lab

This repository contains a collection of Python scripts and JavaScript files designed to automate various processes and tasks in Slack, including managing channels, users, user groups, and Slack workflows.

## Table of Contents
  - [Table of Contents](#table-of-contents)
  - [Scripts Overview](#scripts-overview)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [License](#license)

## Scripts Overview
Here’s a list of all the scripts in this repository along with their descriptions:

1. **[slack_add_remove_channel.py](slack_add_remove_channel.py)**: Automates the process of adding or removing users from Slack channels.
2. **[slack_add_remove_user_workspace.py](slack_add_remove_user_workspace.py)**: Manages adding or removing users from a Slack workspace.
3. **[slack_add_to_channel.py](slack_add_to_channel.py)**: Adds a specified user to a Slack channel.
4. **[slack_add_user_workspace.py](slack_add_user_workspace.py)**: Adds users to a Slack workspace.
5. **[slack_allowlists.py](slack_allowlists.py)**: Manages allowlists for approved users and apps in Slack.
6. **[slack_chan_exp_integration.py](slack_chan_exp_integration.py)**: Integrates Slack channel expiration policies and settings with other systems.
7. **[slack_chanID_name.py](slack_chanID_name.py)**: Exports Slack channel IDs and names for easy reference.
8. **[slack_chanMem_export_userids.py](slack_chanMem_export_userids.py)**: Exports user IDs from Slack channel members.
9. **[slack_chanMem_export.py](slack_chanMem_export.py)**: Exports Slack channel members.
10. **[slack_channel_add.py](slack_channel_add.py)**: Adds channels programmatically to a Slack workspace.
11. **[slack_channel_archive-unarchive.py](slack_channel_archive-unarchive.py)**: Archives and unarchives Slack channels.
12. **[slack_channel_delete.py](slack_channel_delete.py)**: Deletes a Slack channel.
13. **[slack_channel_export.py](slack_channel_export.py)**: Exports the data from a Slack channel.
14. **[slack_channel_public_private.py](slack_channel_public_private.py)**: Changes a Slack channel's visibility from public to private or vice versa.
15. **[slack_channel_retention.py](slack_channel_retention.py)**: Configures retention policies for Slack channels.
16. **[slack_channel_workflow_ping.py](slack_channel_workflow_ping.py)**: Pings specific Slack workflows related to channel activity.
17. **[slack_channel_workspace.py](slack_channel_workspace.py)**: Manages Slack channels within a workspace.
18. **[slack_disable_enable_usergroups.py](slack_disable_enable_usergroups.py)**: Disables or enables user groups within Slack.
19. **[slack_emoji_list.py](slack_emoji_list.py)**: Exports a list of emojis used in a Slack workspace.
20. **[slack_empty_channels_alert.py](slack_empty_channels_alert.py)**: Alerts on empty Slack channels.
21. **[slack_export_workspace_all_users.py](slack_export_workspace_all_users.py)**: Exports all users in a Slack workspace.
22. **[slack_external_teams_disconnection.py](slack_external_teams_disconnection.py)**: Manages disconnection of external teams from Slack channels.
23. **[slack_guest_expiration.py](slack_guest_expiration.py)**: Manages guest user expiration dates within Slack.
24. **[slack_guests_wo_exp.js](slack_guests_wo_exp.js)**: Identifies guests in Slack without an expiration date and notifies relevant users.
25. **[slack_inactive_channels_alert.py](slack_inactive_channels_alert.py)**: Alerts when a Slack channel has been inactive for a specified period.
26. **[slack_multichannelGuest+activate.py](slack_multichannelGuest+activate.py)**: Activates multichannel guest users in Slack.
27. **[slack_remove_from_channel.py](slack_remove_from_channel.py)**: Removes a user from a specific Slack channel.
28. **[slack_remove_user_workspace.py](slack_remove_user_workspace.py)**: Removes a user from a Slack workspace.
29. **[slack_update_user_profile.py](slack_update_user_profile.py)**: Updates a user's profile information in Slack.
30. **[slack_user_activate_deactivate.py](slack_user_activate_deactivate.py)**: Automates user activation and deactivation processes in Slack.
31. **[slack_user_byID.py](slack_user_byID.py)**: Retrieves Slack user information by their user ID.
32. **[slack_user_chan_export_updated.py](slack_user_chan_export_updated.py)**: Exports updated user data from Slack channels.
33. **[slack_user_chan_export.py](slack_user_chan_export.py)**: Exports users from Slack channels.
34. **[slack_user_mcg_udpate.py](slack_user_mcg_udpate.py)**: Updates multi-channel guest users in Slack.
35. **[slack_usergroups_list.py](slack_usergroups_list.py)**: Lists all user groups in a Slack workspace.
36. **[slack_workflows_search.py](slack_workflows_search.py)**: Searches and retrieves data related to Slack workflows.
37. **[slackSDK_restrict_approve.py](slackSDK_restrict_approve.py)**: Restricts or approves Slack apps using the Slack SDK.
38. **[slackSDK_revoke.py](slackSDK_revoke.py)**: Revokes Slack apps and integrations using the Slack SDK.

## Requirements
- **Python 3.x**: Ensure that Python 3 is installed on your system.
- **Slack SDK**: Install the [Slack SDK](https://slack.dev/python-slack-sdk/) for Python to interact with the Slack API.
- **API Keys**: You will need a Slack API token to authenticate API requests. Ensure the token has the necessary permissions for the operations you plan to run.

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo-name/slack-automation-scripts.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Slack API tokens and other necessary credentials in environment variables:
   ```bash
   export SLACK_API_TOKEN="your-token-here"
   ```

## Usage
Run the desired script from the command line or integrate it with your automation workflows.

Example:
```bash
python3 slack_add_to_channel.py --channel "channel-id" --user "user-id"
```

## Contributing
Feel free to submit issues or pull requests to improve the functionality of the scripts or add new features. Contributions are welcome!

## License
This project is licensed under the MIT License.
