import argparse
import json
import os
import shutil
import sys
from urllib.parse import unquote

import wikipedia
from tqdm import tqdm

from war_wikipedia import document_to_json


"""
Given a .jsonl of the form where each line is of the form

{"id": int, "title": str}

retrieves the Wikipedia page and saves it as it's own JSON file.
All other fields will be ignored.
"""


def main():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    project_root = os.path.abspath(os.path.realpath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)))))
    parser.add_argument("--data-path", type=str,
                        default=os.path.join(project_root, "conflicts.jsonl"),
                        help="Path to the .jsonl file containing all conflicts"
                             "and their IDs.")
    parser.add_argument("--save-dir", type=str,
                        default=os.path.join(project_root, "data"),
                        help="Directory to save content content as"
                             "text files.")
    args = parser.parse_args()
    assert os.path.exists(args.data_path), "Invalid path {}".format(args.data_path)

    print("Collecting pages:")
    with open(args.data_path, "r") as conflict_jsonl_file:
        conflict_jsonl = json.load(conflict_jsonl_file)

        # This was PetScan's JSON format to get to the conflict IDs...
        conflicts = conflict_jsonl["*"][0]["a"]["*"]

    for conflict in tqdm(conflicts):
        conflict_id = conflict['id']
        conflict_title = conflict['title']
        if conflict_id is None or conflict_title is None:
            continue

        # Save the conflict as a json file.
        conflict_path = os.path.join(args.save_dir, conflict_title + ".json")
        if os.path.exists(conflict_path):
            continue

        # Collect and process the raw Wikipedia content.
        try:
            conflict_page = wikipedia.page(pageid=conflict_id)
        except AttributeError:
            conflict_page = wikipedia.page(title=conflict_title)
        except:  # pylint: disable=W0702
            print("Failed to collect {}".format(conflict_title))
            continue

        conflict_as_json = document_to_json(conflict_page.content,
                                            title=conflict_title)

        with open(conflict_path, 'w') as outfile:
            json.dump(conflict_as_json, outfile, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()
