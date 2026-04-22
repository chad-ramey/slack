"""
================================================================================
  slack_reinvite_user.py — Bulk re-add a Slack user to channels
================================================================================

WHAT THIS SCRIPT DOES
---------------------
Re-adds a single Slack user to every channel listed in a CSV file.
It skips archived channels, handles rate limiting automatically, and writes
a full results CSV so you know exactly what happened to every channel.

--------------------------------------------------------------------------------
FIRST-TIME SETUP (do this once)
--------------------------------------------------------------------------------

Step 1 — Install Python
  If you don't have Python installed, download it from https://python.org
  (version 3.8 or newer). On a Mac you can also run: brew install python

Step 2 — Install the Slack SDK library
  Open Terminal and run:
    pip install slack_sdk

Step 3 — Create a Slack App with the right permissions
  a. Go to https://api.slack.com/apps and click "Create New App"
  b. Choose "From scratch", give it a name, select your workspace
  c. In the left sidebar click "OAuth & Permissions"
  d. Scroll to "User Token Scopes" and add ALL of the following:
       - admin.conversations:write
       - users:read
       - users:read.email
  e. Scroll up and click "Install to Workspace" — approve it
  f. Copy the "User OAuth Token" (starts with xoxp-)
     IMPORTANT: This token must belong to a Workspace Admin account

Step 4 — Set your token as an environment variable
  In Terminal run (replace the value with your actual token):
    export SLACK_ADMIN_TOKEN="xoxp-your-token-here"

  To avoid re-entering it every session, add that line to ~/.zshrc or ~/.bashrc

--------------------------------------------------------------------------------
PREPARING YOUR CSV FILE
--------------------------------------------------------------------------------
The input CSV must have these exact column headers (order doesn't matter):

  channel_name, channel_id, private, archived, externally_shared

You can export this from the Slack admin console, or generate it with the
companion channel-export script. The channel_id column (e.g. C0A6ADGV6TU)
is what's actually used for the API calls — channel_name is just for logging.

Archived channels are automatically skipped.

--------------------------------------------------------------------------------
RUNNING THE SCRIPT
--------------------------------------------------------------------------------
Basic usage — edit the CONFIG section below, then run:
  python slack_reinvite_user.py

Or pass everything via command-line arguments (no file editing needed):
  python slack_reinvite_user.py --email jane@example.com --input channels.csv

All options:
  --email     Email address of the user to re-add
  --user-id   Slack user ID (e.g. U0AUAP43FNJ) — skips the email lookup
  --input     Path to input CSV file
  --output    Path to write results CSV (default: reinvite_results.csv)
  --delay     Seconds to wait between API calls (default: 2)
  --dry-run   Print what would happen without making any API calls

Examples:
  python slack_reinvite_user.py --email john@company.com --input channels.csv
  python slack_reinvite_user.py --user-id U0AUAP43FNJ --input channels.csv --dry-run
  python slack_reinvite_user.py --email jane@company.com --output june_results.csv

--------------------------------------------------------------------------------
RESULTS CSV COLUMNS
--------------------------------------------------------------------------------
  channel_name       Human-readable channel name
  channel_id         Slack internal channel ID
  status             One of: success | already_in_channel | skipped-archived |
                              channel_not_found | cant_invite_self | failed
  error              Raw error code from Slack if something went wrong

--------------------------------------------------------------------------------
TROUBLESHOOTING
--------------------------------------------------------------------------------
  "SLACK_ADMIN_TOKEN not set"
    → Run: export SLACK_ADMIN_TOKEN="xoxp-..."

  "not_in_channel" or "channel_not_found"
    → The channel ID in your CSV may be stale. Re-export the channel list.

  "not_an_admin"
    → The token you're using doesn't belong to a Workspace Admin account.

  "missing_scope"
    → Re-check Step 3d above. All three scopes must be added as User Token Scopes.

  Rate limiting (script pauses and retries automatically)
    → Increase --delay if you see frequent pauses (try --delay 5)

--------------------------------------------------------------------------------
Author: Chad Ramey (assisted by Claude)
Last Updated: April 22, 2026
--------------------------------------------------------------------------------
"""

import os
import sys
import csv
import time
import logging
import argparse

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ============================================================
#  CONFIG — edit these defaults if you're not using CLI args
# ============================================================
DEFAULT_EMAIL    = "user@example.com"
DEFAULT_INPUT    = os.path.join(os.path.dirname(__file__), "channels.csv")
DEFAULT_OUTPUT   = os.path.join(os.path.dirname(__file__), "reinvite_results.csv")
DEFAULT_DELAY    = 2   # seconds between API calls; increase if you hit rate limits
# ============================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bulk re-add a Slack user to channels listed in a CSV file."
    )
    parser.add_argument("--email",    default=DEFAULT_EMAIL,  help="Email of the user to re-add")
    parser.add_argument("--user-id",  default=None,           help="Slack user ID — skips email lookup")
    parser.add_argument("--input",    default=DEFAULT_INPUT,  help="Path to input CSV file")
    parser.add_argument("--output",   default=DEFAULT_OUTPUT, help="Path to write results CSV")
    parser.add_argument("--delay",    default=DEFAULT_DELAY,  type=float, help="Seconds between API calls")
    parser.add_argument("--dry-run",  action="store_true",    help="Preview actions without calling the API")
    return parser.parse_args()


def get_slack_token():
    token = os.getenv("SLACK_ADMIN_TOKEN")
    if not token:
        print("\nError: SLACK_ADMIN_TOKEN environment variable is not set.")
        print("Run this in your terminal first:")
        print('  export SLACK_ADMIN_TOKEN="xoxp-your-token-here"\n')
        sys.exit(1)
    return token


def lookup_user_by_email(client, email):
    try:
        response = client.users_lookupByEmail(email=email)
        user_id = response["user"]["id"]
        logging.info(f"Resolved {email} → {user_id}")
        return user_id
    except SlackApiError as e:
        logging.error(f"Could not find Slack user for '{email}': {e.response['error']}")
        logging.error("Make sure the email is correct and the token has users:read.email scope.")
        sys.exit(1)


def invite_user(client, channel_id, user_id):
    """Invite user to a channel. Returns (status, error_detail).

    The admin endpoint returns 'failed_for_some_users' for several conditions
    (including already_in_channel) — we parse the per-user reason from
    'failed_user_ids' in the response body to get the real status.
    """
    try:
        client.admin_conversations_invite(channel_id=channel_id, user_ids=[user_id])
        return "success", ""

    except SlackApiError as e:
        error = e.response["error"]

        # The admin endpoint wraps per-user errors here instead of top-level
        if error == "failed_for_some_users":
            reason = e.response.get("failed_user_ids", {}).get(user_id, "failed_for_some_users")
            if reason == "already_in_channel":
                return "already_in_channel", reason
            return "failed", reason

        # Slack asks us to wait — retry once after the specified delay
        if error == "ratelimited":
            retry_after = int(e.response.get("headers", {}).get("Retry-After", 30))
            logging.warning(f"Rate limited — waiting {retry_after}s then retrying...")
            time.sleep(retry_after)
            return invite_user(client, channel_id, user_id)

        if error == "already_in_channel":
            return "already_in_channel", error
        if error == "cant_invite_self":
            return "cant_invite_self", error
        if error == "channel_not_found":
            return "channel_not_found", error

        return "failed", error


def main():
    args = parse_args()

    if args.dry_run:
        logging.info("DRY RUN — no API calls will be made.")

    client = WebClient(token=get_slack_token())

    # Resolve user ID — use --user-id directly if provided, otherwise look up by email
    user_id = args.user_id if args.user_id else lookup_user_by_email(client, args.email)
    logging.info(f"Target user ID: {user_id}")

    counts = {
        "succeeded":       0,
        "already_member":  0,
        "skipped_archived": 0,
        "not_found":       0,
        "failed":          0,
    }
    results = []

    # Load channel list from CSV
    try:
        with open(args.input, mode="r") as csvfile:
            rows = list(csv.DictReader(csvfile))
    except FileNotFoundError:
        logging.error(f"Input CSV not found: {args.input}")
        logging.error("Check the --input path or update DEFAULT_INPUT in the CONFIG section.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to read input CSV: {e}")
        sys.exit(1)

    logging.info(f"Loaded {len(rows)} channels from {args.input}")

    for row in rows:
        name       = row["channel_name"].strip()
        channel_id = row["channel_id"].strip()
        is_archived = row["archived"].strip().lower() == "true"

        # Archived channels can't be joined — skip them
        if is_archived:
            logging.info(f"Skipping '{name}' (archived)")
            counts["skipped_archived"] += 1
            results.append({"channel_name": name, "channel_id": channel_id,
                            "status": "skipped-archived", "error": "archived"})
            continue

        if args.dry_run:
            logging.info(f"[DRY RUN] Would invite to '{name}' ({channel_id})")
            results.append({"channel_name": name, "channel_id": channel_id,
                            "status": "dry-run", "error": ""})
            continue

        status, error = invite_user(client, channel_id, user_id)

        # Pause between calls to stay within Slack's rate limits
        time.sleep(args.delay)

        if status == "success":
            logging.info(f"✓ Invited to '{name}' ({channel_id})")
            counts["succeeded"] += 1
        elif status == "already_in_channel":
            logging.info(f"Already member: '{name}' ({channel_id})")
            counts["already_member"] += 1
        elif status == "channel_not_found":
            logging.warning(f"Channel not found: '{name}' ({channel_id})")
            counts["not_found"] += 1
        elif status == "cant_invite_self":
            logging.warning(f"Can't invite self: '{name}' ({channel_id})")
            counts["failed"] += 1
        else:
            logging.error(f"Failed '{name}' ({channel_id}): {error}")
            counts["failed"] += 1

        results.append({"channel_name": name, "channel_id": channel_id,
                        "status": status, "error": error})

    # Write results to CSV
    with open(args.output, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["channel_name", "channel_id", "status", "error"])
        writer.writeheader()
        writer.writerows(results)

    print("\n=== Summary ===")
    print(f"  Succeeded:          {counts['succeeded']}")
    print(f"  Already member:     {counts['already_member']}")
    print(f"  Skipped (archived): {counts['skipped_archived']}")
    print(f"  Not found:          {counts['not_found']}")
    print(f"  Failed:             {counts['failed']}")
    print(f"\nFull results written to: {args.output}")


if __name__ == "__main__":
    main()
