#!/bin/bash

# Check that the server exists.
server=192.168.1.20
if ! ping -c 1 "$server"; then
    echo "No connection to server. Exiting."
    exit 1
fi

if [ ! -d "/mnt/SharedFolder" ]; then
  sudo mkdir /mnt/SharedFolder
  echo "'/mnt/SharedFolder' created."
fi

sudo mount -t cifs //192.168.1.20/SharedFolder /mnt/SharedFolder -o username=henry,password=46472,uid=1000,gid=1000

source="/home/deck/.local/share/Steam/userdata/96470878/760/remote/"
target="/var/mnt/SharedFolder/Henry/Backups/Media/Game Screenshots/steamdeck"

# Removes trailing "/" characters.
source=$(echo "$source" | sed 's/\/$//')
target=$(echo "$target" | sed 's/\/$//')

# Checks that the source and target exist.
if ! [[ -d "$source" ]]; then
    echo "Source does not exist. Exiting."
    exit 1
elif ! [[ -d "$target" ]]; then
    echo "Target does not exist. Exiting."
    exit 1
fi


overwrite="True"
condition="Recently Modified"
dry_run="False"

path_to_repo="/home/deck/Software/automated_backup/"


# Required for an immutable system.
cd $path_to_repo
. venv/bin/activate


# Call the Python script with Click arguments
"$path_to_repo"backend/backend.py "$source" "$target" --overwrite "$overwrite" --condition "$condition" --dry_run "$dry_run"

sudo umount /mnt/SharedFolder
