"""
Utility to extract all tags from a given .kds file
"""

import json
import os
import sys
from pathlib import Path

# Make the util directory root if not already
os.chdir(Path(__file__).parents[0].resolve())

# Add parent folder to path so we can import filters
sys.path.append("..")

from filters import get_word_tags

# Global variable to save all tags found
tags_found = set()


def save_tags(file_path):
    global tags_found

    file_path.parent.mkdir(exist_ok=True, parents=True)
    with open(file_path, "w", encoding="utf-8") as f:
        # * Sort tags alphabetically
        sorted_tags = sorted(tags_found)
        for tag in sorted_tags:
            f.write((f"{tag}\n"))


def load_last_tags(extracted_tags_file):
    global tags_found

    if not extracted_tags_file.exists():
        print(f'File "{extracted_tags_file}" does not exists')
        return

    with open(f"{extracted_tags_file}", "r", encoding="utf-8") as f:
        for line in f:
            tags_found.add(line.strip("\n"))


def extract_tags(kds_set_file):
    global tags_found

    if not kds_set_file.exists():
        print(f'File "{kds_set_file}" does not exists')
        return

    print(f"Extracting tags from: {kds_set_file}")
    with open(f"{kds_set_file}", "r", encoding="utf-8") as f:
        # every line is a JSON object
        for line_number, line in enumerate(f, 1):
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                print(f"Error parsing {kds_set_file.name} at line {line_number}")
                continue
            data = json.loads(line)
            tags = get_word_tags(data=data)
            for tag in tags:
                tags_found.add(tag)


def extract_from_all_wordsets(wordsets_json_path, extracted_tags_file):
    """
    Use wordsets.json located in '../sets' to
    loop and extract all tags the wordsets listed
    """
    with open(wordsets_json_path, mode="r", encoding="utf-8") as f:
        wordsets = json.load(f)

    for set in wordsets:
        for kds_set in [set["noun"], set["adj"]]:
            kds_set_file = Path(kds_set).resolve()
            extract_tags(kds_set_file)

    save_tags(extracted_tags_file)


if __name__ == "__main__":
    # File to save extracted tags
    # If already exists, previous tags will be also loaded
    extracted_tags_file = Path(f"./_tags.txt").resolve()

    # Sets folder path (the one with .kds files)
    # If no wordsets.json exists, then run build_data.py before executing this script
    wordsets_json_path = Path("../sets")

    if extracted_tags_file.exists():
        print("Extracted tags found, loading last extracted tags")
        load_last_tags(extracted_tags_file)

    # * Loop only one set
    # kds_file = Path(wordsets_json_path / "en_adj.kds").resolve()
    # extract_tags(kds_file)
    # save_tags(extracted_tags_file)

    if not wordsets_json_path.exists():
        print(
            """No wordsets.json file found,
            please run build_data.py before executing this script"""
        )
        sys.exit(1)

    # * Loop all sets
    wordsets_json_path = Path(wordsets_json_path / "wordsets.json").resolve()
    extract_from_all_wordsets(wordsets_json_path, extracted_tags_file)
