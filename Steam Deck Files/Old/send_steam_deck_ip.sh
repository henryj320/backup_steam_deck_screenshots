#!/bin/bash

# Check that the server exists.
server=192.168.1.20
if ! ping -c 1 "$server"; then
    echo "No connection to server. Exiting."
    exit 1
fi

# Create the momunt location if required.
if [ ! -d "/mnt/SharedFolder" ]; then
  sudo mkdir /mnt/SharedFolder
  echo "'/mnt/SharedFolder' created."
fi

sudo mount -t cifs //192.168.1.20/SharedFolder /mnt/SharedFolder -o username=henry,password=46472,uid=1000,gid=1000


# Specify the output file.
output_file="/mnt/SharedFolder/Henry/Logs/steam_deck_ip.txt"

# Get the IP address.
ip_address=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '^127\.')


# Check if IP address was successfully retrieved.
if [ -n "$ip_address" ]; then
  # Write the IP address to the output file
  echo "$ip_address" > "$output_file"
  echo "IP address saved to $output_file"
else
  echo "Failed to retrieve IP address."
fi

# sudo umount /mnt/SharedFolder
