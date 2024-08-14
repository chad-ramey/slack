/**
 * Script: notifySlackAboutGuestsWithoutExpiration
 * 
 * Description:
 * This script identifies active guest users in a Slack workspace who do not have an expiration date set. 
 * It uses the Slack API's admin.users.list method to fetch user data and filters for guests without 
 * the 'expiration_ts' attribute. The results are then posted to a specified Slack channel.
 *
 * Requirements:
 * - The script requires a user token with appropriate permissions, including 'admin.users:read' 
 *   and 'chat:write'.
 * - The Slack token and other sensitive information should be stored securely using 
 *   Google Apps Script's PropertiesService.
 * - Ensure the 'teamId' and 'channel' variables are correctly set to match your Slack workspace and target channel.
 * - The script uses pagination to handle large user lists, retrieving up to 100 users per request.
 *
 * Note:
 * - The script uses a user token instead of a bot token as some administrative actions require 
 *   user-level permissions.
 * - Replace placeholder values with actual tokens and IDs.
 *
 * Author: Chad Ramey
 * Date: July 29, 2024
 */

function notifySlackAboutGuestsWithoutExpiration() {
  try {
    var token = PropertiesService.getScriptProperties().getProperty('SLACK_USER_TOKEN');
    var teamId = ""; // Replace with your actual Slack team ID
    var channel = ""; // Replace with your Slack channel ID
    var url = "https://slack.com/api/admin.users.list";
    var guestsWithoutExpiration = [];
    var cursor = "";
    var limit = 100; // Slack API allows a maximum of 100 users per page

    if (!token) {
      Logger.log('SLACK_USER_TOKEN is missing in script properties.');
      return;
    }

    if (!teamId) {
      Logger.log('Team ID is missing.');
      return;
    }

    do {
      // Prepare the payload
      var payload = {
        token: token,
        team_id: teamId,
        limit: limit
      };

      if (cursor) {
        payload.cursor = cursor;
      }

      // Convert the payload object to URL-encoded string
      var formData = encodeQueryData(payload);

      // Fetch users data from Slack using admin.users.list
      var response = UrlFetchApp.fetch(url, {
        method: "post",
        headers: {
          "Authorization": "Bearer " + token,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        payload: formData
      });

      var data = JSON.parse(response.getContentText());

      if (!data.ok) {
        Logger.log('Error fetching data from Slack API: ' + data.error);
        Logger.log('Response: ' + response.getContentText());
        return;
      }

      var users = data.users;
      cursor = (data.response_metadata && data.response_metadata.next_cursor) ? data.response_metadata.next_cursor : "";

      if (!users || !Array.isArray(users)) {
        Logger.log('Unexpected data structure for users: ' + JSON.stringify(data));
        return;
      }
      
      Logger.log('Total users retrieved in this batch: ' + users.length);

      users.forEach(function(user) {
        Logger.log('Processing user: ' + JSON.stringify(user));

        if (user.is_deleted) {
          Logger.log('Skipping user (deleted): ' + user.id);
          return;
        }

        if (!user.is_restricted && !user.is_ultra_restricted) {
          Logger.log('Skipping user (not a guest): ' + user.id);
          return;
        }

        if (user.email && user.email.endsWith("@domain.com")) {
          Logger.log('Skipping user (OnePeloton email): ' + user.id);
          return;
        }

        // Check for no expiration status
        if (user.expiration_ts == 0 || user.expiration_ts === undefined) {
          var creationTime = 'Unknown';
          if (user.date_created) {
            try {
              creationTime = new Date(user.date_created * 1000).toISOString();
            } catch (e) {
              Logger.log('Error processing creation date for user ' + user.id + ': ' + e.message);
            }
          } else {
            Logger.log('No creation date for user ' + user.id);
          }

          guestsWithoutExpiration.push({
            email: user.email,
            creation_time: creationTime,
            name: user.full_name,
            id: user.id
          });
        }
      });

    } while (cursor);

    Logger.log('Guests without expiration found: ' + guestsWithoutExpiration.length);
    if (guestsWithoutExpiration.length > 0) {
      var message = "Active guests without expiration:\n" +
                    guestsWithoutExpiration.map(g => 
                      `*Email*: ${g.email}\n*Name*: ${g.name}\n*Creation Time*: ${g.creation_time}\n*User ID*: ${g.id}`
                    ).join("\n\n");

      postToSlack(channel, message, token);
    } else {
      Logger.log('No active guests without expiration found.');
    }
  } catch (e) {
    Logger.log('An error occurred: ' + e.message);
  }
}

function encodeQueryData(data) {
  const ret = [];
  for (let d in data)
    if (data[d] !== undefined) {
      ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
    }
  return ret.join('&');
}

function postToSlack(channel, message, token) {
  var url = "https://slack.com/api/chat.postMessage";
  var payload = {
    channel: channel,
    text: message
  };

  var options = {
    method: "post",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    payload: JSON.stringify(payload)
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    var result = JSON.parse(response.getContentText());

    if (!result.ok) {
      Logger.log('Error posting to Slack: ' + result.error);
      Logger.log('Full response: ' + response.getContentText());
    } else {
      Logger.log('Message posted successfully to Slack channel ' + channel);
    }
  } catch (e) {
    Logger.log('An error occurred while posting to Slack: ' + e.message);
  }
}
