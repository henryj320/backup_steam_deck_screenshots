#!/bin/bash

server_directory="/home/casa/locations/games/Screenshots/steamdeck/remote/"
pull_user="deck"
pull_directory="/home/deck/.local/share/Steam/userdata/96470878/760/remote/"

# Get pull_ip.
ip_file="/home/casa/locations/games/Screenshots/IPs/steamdeck.txt"
if [[ ! -f "$ip_file" ]]; then
    echo "Error: IP file not found at $ip_file"
    exit 1
fi
pull_ip="$(cat "$ip_file" | tr -d '[:space:]')"

# Check pull_ip is reachable.
ping -c 2 "$pull_ip" &>/dev/null
if [[ $? -ne 0 ]]; then
    echo "Error: Device at $pull_ip is not reachable."
    exit 1
fi

# Check pull_directory exists.
ssh "$pull_user@$pull_ip" "[[ -d '$pull_directory' ]]" 
if [[ $? -ne 0 ]]; then
    echo "Error: Directory $pull_directory does not exist on remote device."
    exit 1
fi

# Return number of files to rsync.
files_synced=$(rsync --stats --dry-run -a "$pull_user@$pull_ip:$pull_directory" "$server_directory" | grep "Number of regular files transferred:" | awk '{print $6}')
echo "Files synced: ${files_synced:-0}"

# Rsync screenshots.
rsync -a --ignore-existing "$pull_user@$pull_ip:$pull_directory" "$server_directory"
