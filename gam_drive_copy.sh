#!/bin/bash

# Script to copy Google Drive content from one employee to another using GAMADV-XTD3
# Tested on zsh + bash
# fish version coming soon

echo "Starting the Google Drive transfer process..."

# Ask for the old and new owner's email addresses
read -p "Enter the email address of the old owner: " old_owner
read -p "Enter the email address of the new owner: " new_owner

# 1. Unsuspend old owner
echo "Unsuspending the old owner..."
gam unsuspend user $old_owner

# 2. Create folder in new owner's drive
echo "Creating 'Drive Copy' folder in the new owner's drive..."
folder_creation_output=$(gam user $new_owner create drivefile drivefilename "Drive Copy" mimetype gfolder)
folder_id=$(echo "$folder_creation_output" | awk -F'[()]' '{print $2}')

# Check if folder_id is extracted successfully
if [ -z "$folder_id" ]; then
    echo "Failed to create folder or extract folder ID."
    exit 1
fi

# 3. Add old owner as editor of the Drive Copy folder
echo "Adding old owner as an editor of 'Drive Copy' folder..."
gam user $new_owner add drivefileacl $folder_id user $old_owner role writer

# 4. Find root id of old owner's Drive
echo "Finding root ID of the old owner's Drive..."
old_root_id=$(gam user $old_owner show fileinfo root id | awk '/id:/{print $2}')

# Check if old_root_id is extracted successfully
if [ -z "$old_root_id" ]; then
    echo "Failed to find the root ID of the old owner's Drive."
    exit 1
fi

# 5. Copy old owner's drive to a new subfolder in the new owner's Drive Copy folder
echo "Copying old owner's Drive to a new subfolder in the new owner's 'Drive Copy' folder..."
gam user $old_owner copy drivefile $old_root_id parentid $folder_id newfilename "$old_owner" recursive depth -1

# 6. Transfer ownership of copied files
echo "Transferring ownership of copied files to the new owner..."
gam user $old_owner transfer ownership $folder_id $new_owner

# 7. Remove old owner's access to all copied data in the 'Drive Copy' folder
echo "Removing old owner's access to all copied data in the 'Drive Copy' folder..."

# Command to remove old owner's access from all items in the 'Drive Copy' folder
gam user $new_owner print filelist select id $folder_id fields id showparent | gam csv - gam user "~Owner" delete drivefileacl "~id" $old_owner

# 8. Suspend old owner after completion
echo "Suspending the old owner again..."
gam suspend user $old_owner

echo "Google Drive transfer process completed!"