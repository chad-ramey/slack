#!/bin/bash

# Script to transfer Google Drive file from one employee to another using GAMADV-XTD3
# Tested on zsh + bash
# Todo: fish, multiple files, suspend/unsuspend

# Prompt for the old owner's email address
read -p "Enter old owner's email address: " old_owner_email

# Prompt for the new owner's email address
read -p "Enter new owner's email address: " new_owner_email

# Prompt for the file ID
read -p "Enter the file ID to be transferred: " file_id

# Prompt if old owner should retain access and set the retainrole parameter
read -p "Should the old owner retain access to the file? (yes/no): " retain_access
retain_role="none" # Default to none

if [ "$retain_access" = "yes" ]; then
    # Prompt for the access level for the old owner
    read -p "Choose the access level for the old owner (reader/commenter/writer/editor): " old_owner_access_level
    retain_role="$old_owner_access_level"
fi

# Add the new owner as a writer to the file
gam user "$old_owner_email" add drivefileacl "$file_id" user "$new_owner_email" role writer

# New owner claims ownership of the file with the specified retainrole
gam user "$new_owner_email" claim ownership "$file_id" retainrole "$retain_role"

# If old owner is not supposed to retain access, remove their access
if [ "$retain_access" = "no" ]; then
    gam user "$old_owner_email" delete drivefileacl "$file_id" user "$old_owner_email"
fi

# Find the new owner's drive's root ID
root_id=$(gam user "$new_owner_email" show fileinfo root id | grep 'id:' | awk '{print $2}')

# Move the file to the new owner's drive
gam user "$new_owner_email" move drivefile "$file_id" parentid "$root_id"

echo "File transfer process is complete."
