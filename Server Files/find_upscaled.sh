#!/bin/bash

# Set the base directory to search (default to current directory if not provided)
BASE_DIR="${1:-.}"

# Initialize an array to hold matching directories
matches=()

# Find all directories and check for subdirectories matching "*Upscaled*" (case-insensitive)
while IFS= read -r -d '' dir; do
    if find "$dir" -mindepth 1 -maxdepth 1 -type d -iname "*Upscaled*" | grep -q .; then
        matches+=("$dir")
    fi
done < <(find "$BASE_DIR" -type d -print0)

# Sort and print the results
IFS=$'\n' sorted=($(sort <<<"${matches[*]}"))
unset IFS
printf "%s\n" "${sorted[@]}"
