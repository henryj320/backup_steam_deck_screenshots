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
/home/software/repositories/backup_steam_deck_screenshots/Server\ Files/pull_screenshots.sh
show_progress "Completed pull_screenshots.sh"
echo

show_progress "Filtering Steam Deck screenshots"
python3 /home/software/repositories/backup_steam_deck_screenshots/Organise-Steam-Deck/filter_screenshots.py
show_progress "Completed filter_screenshots.py (Steam-Deck)"
echo

show_progress "Filtering Gaming PC screenshots"
python3 /home/software/repositories/backup_steam_deck_screenshots/Organise-Be-Quiet-PC/filter_screenshots.py
show_progress "Completed filter_screenshots.py (Be-Quiet-PC)"
echo

start_end_progress "🎉 All tasks completed successfully!"
echo
