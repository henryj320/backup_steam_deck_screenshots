"""Filters the screenshots from IDs to named folders."""

import json
import os
import re
import shutil
import time
from datetime import datetime

import requests
from dotenv import load_dotenv  # type: ignore # noqa: F401

# Read the .env variables.
load_dotenv()
source = os.getenv("SOURCE")
dest = os.getenv("DESTINATION")
gameids_file = os.getenv("GAME_IDS_JSON")


def reformat_filename_steamdeck(filename: str) -> str:
    """Matches the filename to a datetime pattern and reformats it.

    Args:
        filename (str): The file to rename.

    Returns:
        str: New name for the file.
    """
    # Regular expression to match datetime pattern in the file name
    match = re.match(r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})_1\.(\w+)", filename)

    if match:
        year, month, day, hour, minute, second, extension = match.groups()
        new_name = f"{year}-{month}-{day} at {hour}-{minute}-{second}.{extension}"
        return new_name
    else:
        return filename


def run_steamdeck(games: list) -> None:
    """Run with commands specialised for the Steam Deck.

    Args:
        games (list): List of game details from game-ids.json.
    """
    directories_created = 0
    images_moved = 0

    destination_path = dest
    current_game = ""
    current_game_id = ""
    subdirectory = ""
    # Copy images from "source/id/screenshots" to "destination/name (year)" if not already copied.
    for root, dirs, files in os.walk(source):
        # Make it so thumbnails aren't copied.
        dirs[:] = [d for d in dirs if d != "thumbnails"]

        for file_name in files:
            source_file = os.path.join(root, file_name)
            new_file_name = reformat_filename_steamdeck(file_name)

            game_id = str(source_file.split(source)[1].split("/")[0])

            # Doesn't recall the SteamAPI unless its a new game.
            if game_id != current_game_id:
                current_game_id = game_id
                game_detail_returned, subdirectory = get_game_details(int(game_id), games)
                if current_game != subdirectory:
                    current_game = subdirectory
                    print(f"Moving on to {current_game}")

            if not game_detail_returned:
                # Failed because missing game ID.
                return

            destination_file = os.path.join(destination_path, subdirectory, new_file_name)
            destination_file_dir = os.path.dirname(destination_file)

            if not os.path.exists(destination_file_dir):
                os.makedirs(destination_file_dir)
                directories_created = directories_created + 1

            # Copy the file over if it doesn't exist.
            if not os.path.exists(destination_file):
                shutil.copy2(source_file, destination_file)
                images_moved = images_moved + 1

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{completed_at} - Created {directories_created} directories and copied {images_moved} images")


def reformat_filename_gamingpc(filename: str) -> str:
    """Matches the filename to a datetime pattern and reformats it.

    Args:
        filename (str): The file to rename.

    Returns:
        str: New name for the file.
    """
    # Regular expression to match datetime pattern in the file name
    match = re.match(r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})", filename)

    if match:
        year, month, day, hour, minute, second = match.groups()
        new_name = f"{year}-{month}-{day} at {hour}-{minute}-{second}.png"
        return new_name
    else:
        return filename


def get_game_details(game_id: int, games: list) -> tuple:
    """Calls the SteamAPI to get game details. Uses game-ids.json if a non-Steam Game.

    Args:
        game_id (int): ID to find the details of.
        games (list): Dict of game-ids.json

    Returns:
        tuple: Whether the request succeeded, and what the game name is.
    """
    game_details_url = f"https://store.steampowered.com/api/appdetails?appids={str(game_id)}"

    try:
        response = requests.get(game_details_url)

        data = response.json()

        # If a non-Steam game.
        try:
            # Required because of Steam-side bug that sets game_id to 9223372036854775807 if number is too large.
            response_success = data[str(game_id)]["success"]
        except KeyError:
            response_success = False
        except TypeError:
            # Looks like the API genuinely returns "null" sometimes. Just have to wait it out.
            response_success = False
            time.sleep(10)

        # Check the JSON file if a non-Steam game
        found = False
        if not response_success:
            for game in games:
                if game["id"] == int(game_id):
                    game_name = game["name"]
                    game_date = game["year"]
                    found = True
                    subdirectory = f"{game_name} ({game_date})"

            if not found:
                print(games)
                print(f"{game_id}")
                return False, ""

            return True, subdirectory

        # Sanitise the name.
        game_name = data[str(game_id)]["data"]["name"]
        game_name = game_name.replace(":", " -")
        game_name = game_name.replace("'", "")
        sanitized_name = re.sub(r'[<>:"/\\|?*©™®]', "", game_name)
        sanitized_name = sanitized_name.strip()

        game_year = data[str(game_id)]["data"]["release_date"]["date"]
        game_year_only = game_year.split(" ")[2]

        return True, f"{sanitized_name} ({game_year_only})"

    except requests.exceptions.RequestException as e:
        print(e)


def run_gamingpc(games: list) -> None:
    """Run with commands for a Linux-based gaming PC.

    Args:
        games (list): List of game details from game-ids.json.
    """
    directories_created = 0
    images_moved = 0

    # Create the directories.
    for game in games:
        game_name = game["name"]
        game_year = game["year"]

        source_path = f"{source}"
        # Change destination based on if the year is set or not.
        destination_path = f"{dest}/{game_name} ({game_year})" if int(game_year) != 0 else f"{dest}/{game_name}"

        # Create the directory if not already created.
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
            directories_created = directories_created + 1

    destination_path = dest
    current_game = ""
    current_game_id = ""
    subdirectory = ""
    # Copy images from "source/id/screenshots" to "destination/name (year)" if not already copied.
    for root, dirs, files in os.walk(source_path):
        # Make it so thumbnails aren't copied.
        dirs[:] = [d for d in dirs if d != "thumbnails"]

        for file_name in files:
            source_file = os.path.join(root, file_name)
            relative_path = os.path.relpath(source_file, source_path)

            game_id = file_name.split("_")[0]

            # Doesn't recall the SteamAPI unless its a new game.
            if game_id != current_game_id:
                current_game_id = game_id
                game_detail_returned, subdirectory = get_game_details(int(game_id), games)

                if current_game != subdirectory:
                    current_game = subdirectory
                    print(f"Moving on to {current_game}")

            if not game_detail_returned:
                # Failed because missing game ID.
                return

            no_gameid = file_name.split("_")[1]

            new_file_name = reformat_filename_gamingpc(no_gameid)
            destination_file = os.path.join(
                destination_path, os.path.dirname(relative_path), subdirectory, new_file_name
            )
            destination_file_dir = os.path.dirname(destination_file)

            # Create the directory if it doesn't exist.
            if not os.path.exists(destination_file_dir):
                os.makedirs(destination_file_dir)
                directories_created = directories_created + 1

            # Copy the file over if it doesn't exist.
            if not os.path.exists(destination_file):
                shutil.copy2(source_file, destination_file)
                images_moved = images_moved + 1

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{completed_at} - Created {directories_created} directories and copied {images_moved} images")


if __name__ == "__main__":
    start_time = time.time()

    # Convert the .json into a Dict.
    with open(gameids_file) as json_file:
        data = json.load(json_file)
    games = data["games"]

    device = os.getenv("DEVICE")
    if device == "DECK":
        run_steamdeck(games)
    if device == "GAMINGPC":
        run_gamingpc(games)

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Time taken: {elapsed:.4f} seconds")
