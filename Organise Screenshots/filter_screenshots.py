"""Filters the screenshots from IDs to named folders."""

import json
import os
import re
import shutil
from datetime import datetime

from dotenv import load_dotenv  # type: ignore # noqa: F401

# Read the .env variables.
load_dotenv()
source = os.getenv("SOURCE")
dest = os.getenv("DESTINATION")
gameids_file = os.getenv("GAME_IDS_JSON")


def reformat_filename(filename: str) -> str:
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


if __name__ == "__main__":
    # Convert the .json into a Dict.
    with open(gameids_file) as json_file:
        data = json.load(json_file)
    games = data["games"]

    directories_created = 0
    images_moved = 0

    # For each item in the Dict:
    for game in games:
        # Record the details.
        game_id = game["id"]
        game_name = game["name"]
        game_year = game["year"]

        source_path = f"{source}/{game_id}/screenshots"
        # Change destination based on if the year is set or not.
        destination_path = f"{dest}/{game_name} ({game_year})" if int(game_year) != 0 else f"{dest}/{game_name}"

        # Create the directory if not already created.
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
            directories_created = directories_created + 1

        # Copy images from "source/id/screenshots" to "destination/name (year)" if not already copied.
        for root, dirs, files in os.walk(source_path):
            # Make it so thumbnails aren't copied.
            dirs[:] = [d for d in dirs if d != "thumbnails"]

            for file_name in files:
                source_file = os.path.join(root, file_name)
                relative_path = os.path.relpath(source_file, source_path)

                new_file_name = reformat_filename(file_name)
                destination_file = os.path.join(destination_path, os.path.dirname(relative_path), new_file_name)
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

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{completed_at} - Created {directories_created} directories and copied {images_moved} images")
