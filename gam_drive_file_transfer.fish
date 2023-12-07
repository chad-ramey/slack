#!/usr/bin/env fish

echo "Starting the Google Drive file transfer process..."

# Ask for the old and new owner's email addresses
echo "Enter the email address of the old owner: "
read old_owner_email
echo "Enter the email address of the new owner: "
read new_owner_email

# Ask for the file ID
echo "Enter the file ID to be transferred: "
read file_id

# Ask if old owner should retain access and set the retainrole parameter
echo "Should the old owner retain access to the file? (yes/no): "
read retain_access
set retain_role "none" # Default to none

if test "$retain_access" = "yes"
    # Ask for the access level for the old owner
    echo "Choose the access level for the old owner (reader/commenter/writer/editor): "
    read old_owner_access_level
    set retain_role $old_owner_access_level
end

# Add the new owner as a writer to the file
gam user "$old_owner_email" add drivefileacl "$file_id" user "$new_owner_email" role writer

# New owner claims ownership of the file with the specified retainrole
gam user "$new_owner_email" claim ownership "$file_id" retainrole "$retain_role"

# If old owner is not supposed to retain access, remove their access
if test "$retain_access" = "no"
    # Use the new owner's email to remove the old owner's access
    gam user "$new_owner_email" delete drivefileacl "$file_id" "$old_owner_email"
end

# Find the new owner's drive's root ID
set root_id (gam user "$new_owner_email" show fileinfo root id | grep 'id:' | awk '{print $2}')

# Move the file to the new owner's drive
gam user "$new_owner_email" move drivefile "$file_id" parentid "$root_id"

echo "Google Drive file transfer process completed!"
