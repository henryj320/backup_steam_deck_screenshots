#!/bin/bash

# Exit immediately if any command fails.
set -e

# Prints progress in blue.
show_progress() {
    echo -e "\e[1;34m$1...\e[0m"
}
start_end_progress() {
    echo -e "\e[1;32m[$(date +'%H:%M:%S')] $1...\e[0m"
}

echo
start_end_progress "⚙️ Starting backup process"

echo
show_progress "Pulling screenshots from Steam Deck"
# /home/software/repositories/backup_steam_deck_screenshots/Server\ Files/pull_screenshots.sh
if /home/software/repositories/backup_steam_deck_screenshots/Server\ Files/pull_screenshots.sh; then
    show_progress "Completed pulling screenshots from Steam Deck"
else
    show_progress "Failed pulling screenshots from Steam Deck. Continuing"
fi
echo

show_progress "Pulling screenshots from Gaming PC"
# /home/software/repositories/backup_steam_deck_screenshots/Server\ Files/pull_screenshots_gaming_pc.sh
if /home/software/repositories/backup_steam_deck_screenshots/Server\ Files/pull_screenshots_gaming_pc.sh; then
    show_progress "Completed pulling screenshots from Gaming PC"
else
    show_progress "Failed pulling screenshots from Gaming PC. Continuing"
fi
echo

show_progress "Filtering Steam Deck screenshots"
python3 /home/software/repositories/backup_steam_deck_screenshots/Organise-Steam-Deck/filter_screenshots.py --nocreate
show_progress "Completed filtering Steam Deck screenshots"
echo

show_progress "Filtering Gaming PC screenshots"
python3 /home/software/repositories/backup_steam_deck_screenshots/Organise-Be-Quiet-PC/filter_screenshots.py --nocreate
show_progress "Completed filtering Gaming PC screenshots"
echo

start_end_progress "🎉 All tasks completed successfully!"
echo

curl -d "Whale Server - Automatic pull and filter complete" ntfy.sh/whale_server_1
