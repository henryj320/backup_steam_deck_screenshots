# backup_steam_deck_screenshots

Last update: 2024-11-30 22:15
<br><br>

A small repository containing the service files, timers and Python scripts required to back up Steam Deck pictures onto an alternative location.

## backup_steam_deck_screenshots

**Title**: backup_steam_deck_screenshots

**Date Started**: 2024-10-10

**Date Completed**: 2024-10-11

**Language**: Python, Bash, Systemctl

---

## Running the Project

### Steam Deck

Screenshots are uploaded to the server using a Bash script.

There is also *.service* and *.timer* files to allow regularly scheduling the upload. To set up files to regularly upload, follow these steps:

1. Adjust the Bash script as required. Make sure it is executable with ` chmod +x `.
2. Copy the *.service* and *.timer* files into "/home/deck/.config/systemd/user/".
3. Run these commands:

```bash
# Pick up the new files.
systemctl --user daemon-reload

# Start the service and timer.
systemctl --user start sync_screenshots.service
systemctl --user start sync_screenshots.timer

# Allow the files to run on restart.
systemctl --user enable sync_screenshots.service
systemctl --user enable sync_screenshots.timer

# Check that the timer is running.
systemctl --user list-timers --all
```

You can also check the logs with ` journalctl --user -xe -u sync_screenshots `.

### Server-Side

Once the screenshots are present on the server, then can be organised. Follow this process to filter the screenshots:

1. ` cd "Organise Screenshots" `.
2. ` pip install -r requirements.txt `.
3. Update *.env* as required.
4. ` python ./filter_screenshots.py `.

The end result is a directory containing all of the screenshots organised by game.

![Filtered Screenshots directory](Images/Filtered%20Screenshots.png)
