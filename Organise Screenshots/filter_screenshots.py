"""Filters the screenshots from IDs to named folders."""

import argparse
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


def run_steamdeck(games: list, nocreate: bool) -> None:  # noqa: C901, PLR0912
    """Filter images based on the default Steam Deck folder layout.

    Args:
        games (list): List of dicts from game-ids.json
        nocreate (bool): Whether or not to add new items to game-ids.json. False for automated runs.
    """
    source_path = f"{source}"

    for root, dirs, files in os.walk(source_path):
        # Make it so thumbnails aren't copied.
        dirs[:] = [d for d in dirs if d != "thumbnails"]

        # If a root game directory.
        if len(dirs) > 0:
            # Get the game ID
            game_id = os.path.relpath(root, source)

            # Skip for top level.
            if game_id == ".":
                continue

            # Find those already in game-ids.json.
            in_json = False
            for game in games:
                if game["id"] == int(game_id):
                    in_json = True

            # Add game to game-ids.json if wanted.
            if not in_json:
                print(f"Game ID not present in game-ids.json: {game_id}")
                print(f"\nPredicted game name:\n{predict_game(game_id)}")
                if nocreate:
                    print("Exiting now, nocreate set to True")
                    return
                else:
                    response = input("Is this name correct? (y/n): ").strip().lower()
                    if response == "y":
                        add_game_to_json(gameids_file, int(game_id), predict_game(game_id))
                        print("Added to game-ids.json. Rerun script now.")
                    else:
                        c_name = input("What is the correct name? ").strip()
                        c_year = input("What is the correct year? ").strip().lower()
                        try:
                            if c_year == "":
                                add_game_to_json(gameids_file, int(game_id), f"{c_name}")
                            else:
                                add_game_to_json(gameids_file, int(game_id), f"{c_name} ({c_year})")
                        except Exception:
                            print("game-ids.json not updated.")
                    return

        # Actually create the directories and move the files.
        directories_created = 0
        images_moved = 0
        for game in games:
            # Record the details.
            game_id = game["id"]
            game_name = game["name"]
            game_year = game["year"]
            destination_path = f"{dest}/{game_name} ({game_year})" if int(game_year) != 0 else f"{dest}/{game_name}"
            for file_name in files:
                # If the Game ID matches one in game-ids.json.
                if game_id == int(os.path.relpath(root, source).split("/")[0]):
                    source_file = os.path.join(root, file_name)

                    new_file_name = reformat_filename_steamdeck(file_name)
                    destination_file = os.path.join(destination_path, new_file_name)
                    destination_file_dir = os.path.dirname(destination_file)

                    # Create the directory if it doesn't exist.
                    if not os.path.exists(destination_file_dir):
                        os.makedirs(destination_file_dir)
                        directories_created = directories_created + 1

                    # Copy the file over if it doesn't exist.
                    if not os.path.exists(destination_file):
                        shutil.copy2(source_file, destination_file)
                        # print(f"Copied: {source_file} -> {destination_file}")
                        images_moved = images_moved + 1

                    continue

    return

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


def run_gamingpc(games: list, nocreate: bool) -> None:  # noqa: C901, PLR0912
    """Filter images based on a Linux-based gaming PC.

    Args:
        games (list): List of dicts from game-ids.json
        nocreate (bool): Whether or not to add new items to game-ids.json. False for automated runs.
    """
    directories_created = 0
    images_moved = 0

    # For each item in the Dict:
    for game in games:
        # Record the details.
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
    # Copy images from "source/id/screenshots" to "destination/name (year)" if not already copied.
    for root, dirs, files in os.walk(source_path):
        # Make it so thumbnails aren't copied.
        dirs[:] = [d for d in dirs if d != "thumbnails"]

        for file_name in files:
            source_file = os.path.join(root, file_name)
            relative_path = os.path.relpath(source_file, source_path)

            game_id = file_name.split("_")[0]
            found = False
            for game in games:
                if game["id"] == int(game_id):
                    game_name = game["name"]
                    game_date = game["year"]
                    found = True
                    subdirectory = f"{game_name} ({game_date})"

            if not found:
                print(f"Game ID not present in game-ids.json: {game_id}")
                print(f"\nPredicted game name:\n{predict_game(game_id)}")
                if nocreate:
                    print("Exiting now, nocreate set to True")
                    return
                else:
                    response = input("Is this name correct? (y/n): ").strip().lower()
                    if response == "y":
                        add_game_to_json(gameids_file, int(game_id), predict_game(game_id))
                        print("Added to game-ids.json. Rerun script now.")
                    else:
                        print("game-ids.json not updated.")
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


def predict_game(game_id: str) -> str:
    """Call Steam API to predict game name and year.

    Args:
        game_id (str): Stringified game ID.

    Returns:
        str: Game name and year. E.g. "Marvel Rivals (2024)".
    """
    # Call the Steam API to get the game name.
    url = f"https://store.steampowered.com/api/appdetails?appids={game_id}"
    response = requests.get(url)
    data = response.json()
    app_data = data.get(str(game_id), {}).get("data", {})

    # Exit if no game found.
    game_data = data.get(str(game_id))
    if not game_data or not game_data.get("success"):
        return None

    name = app_data.get("name", None)
    release_date_str = app_data.get("release_date", {}).get("date", "")

    # Clean up the name.
    name = name.replace(":", " -")
    name = name.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    name = name.replace("'s", "s -")
    name = name.replace("'", "")

    name = re.sub(r"[®™©]", "", name)
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip()

    # Extract year using regex.
    match = re.search(r"\b(19|20)\d{2}\b", release_date_str)
    year = match.group(0) if match else None

    if name and year:
        return f"{name} ({year})"
    elif name:
        return name
    else:
        return None


def add_game_to_json(gameids_file: str, game_id: int, directory_name: str) -> bool:
    """Add the new game to game-ids.json.

    Args:
        gameids_file (str): Path to game-ids.json.
        game_id (int): Game ID to add.
        directory_name (str): Game ID and year in the appropriate format.

    Returns:
        bool: _description_
    """
    match = re.match(r"^(.*?)\s*\((\d{4})\)$", directory_name)
    if not match:
        print("Directory name format should be 'Game Name (Year)'")
        return False

    name, year_str = match.groups()
    year = int(year_str)

    # Load existing data
    if os.path.exists(gameids_file):
        with open(gameids_file, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"games": []}

    # Check for duplicate
    if any(game["id"] == game_id for game in data["games"]):
        print(f"Game ID {game_id} already exists.")
        return False

    # Append new game
    data["games"].append({"id": game_id, "name": name.strip(), "year": year})

    # Write back
    with open(gameids_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Game '{name.strip()}' ({year}) added.")
    return True


def parse_args():
    """Take in the --nocreate argument."""
    parser = argparse.ArgumentParser(description="Filter screenshots with optional flags")
    parser.add_argument(
        "--nocreate", action="store_true", help="If set, disables creating directories (sets nocreate=True)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    start_time = time.time()
    args = parse_args()
    nocreate = args.nocreate

    # Convert the .json into a Dict.
    with open(gameids_file) as json_file:
        data = json.load(json_file)
    games = data["games"]

    device = os.getenv("DEVICE")
    if device == "DECK":
        run_steamdeck(games, nocreate)
    if device == "GAMINGPC":
        run_gamingpc(games, nocreate)

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Time taken: {elapsed:.4f} seconds")

    # python -m ruff format .
