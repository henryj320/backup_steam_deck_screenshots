#!/bin/bash

# Variables.
remote_user="casa"
remote_server=192.168.1.20
remote_directory="/home/casa/locations/games/Screenshots/test-steamdeck/"

source="/home/deck/.local/share/Steam/userdata/96470878/760/remote/"
# source="/home/henry/Documents/Repositories/backup_steam_deck_screenshots/Steam Deck Files/test-input/"
if_exists="skip"


# Check source directory exists.
if [ ! -d "$source" ]; then
    echo "Error: Source directory does not exist."
    exit 1
fi

# Check that the server is reachable.
ping -c 1 "$remote_server" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Remote server is unreachable."
    exit 1
fi

# Check that the remote directory exists.
ssh "$remote_user@$remote_server" "[ -d \"$remote_directory\" ]" 
if [ $? -ne 0 ]; then
    echo "Error: Remote directory does not exist."
    exit 1
fi

# Adjust rsync flags.
rsync_flags="-a"
if [ "$if_exists" == "skip" ]; then
    rsync_flags="$rsync_flags --ignore-existing"
fi

# Return number of files rsynced.
files_synced=$(rsync --stats --dry-run $rsync_flags "$source" "$remote_user@$remote_server:$remote_directory" | grep "Number of regular files transferred:" | awk '{print $6}')
echo "Files synced: ${files_synced:-0}"

# Rsync screenshots.
rsync $rsync_flags "$source" "$remote_user@$remote_server:$remote_directory"


# --------------------------------------------------------------------------


# Get this device's local IP address.
device_ip=$(ip route get 1.1.1.1 | awk '{print $7; exit}')

# Get this device's hostname.
device_hostname=$(cat /etc/hostname 2>/dev/null || cat /proc/sys/kernel/hostname 2>/dev/null)

remote_ip_directory="/home/casa/locations/games/Screenshots/IPs/"

# Check that the directory exists.
ssh "$remote_user@$remote_server" "[ -d \"$remote_ip_directory\" ]" 
if [ $? -ne 0 ]; then
    echo "Error: Remote IP directory does not exist."
    exit 1
fi

# Output the local IP into <hostname>.txt in remote_ip_directory.
echo "$device_ip" | ssh "$remote_user@$remote_server" "cat > $remote_ip_directory/${device_hostname}.txt"
