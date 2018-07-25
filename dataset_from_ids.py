import argparse
import os
import shutil
import sys
from urllib.parse import unquote

import wikipedia
from tqdm import tqdm

import json

from war_wikipedia import document_to_json


"""
Given a .jsonl of the form where each line is of the form {"id": int, "title": str},
retrieves the Wikipedia page and saves it as it's own JSON file. All other fields will be ignored.
"""


def main():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    project_root = os.path.abspath(os.path.realpath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)))))
    parser.add_argument("--data-path", type=str,
                        default=os.path.join(project_root, "conflicts.jsonl"),
                        help="Path to the .jsonl file containing all conflicts and their IDs.")
    parser.add_argument("--save-dir", type=str,
                        default=os.path.join(project_root, "data"),
                        help="Directory to save content content as"
                             "text files.")
    args = parser.parse_args()
    assert os.path.exists(args.data_path), "Invalid path {}".format(args.data_path)
    print("Collecting pages:")
    for line in tqdm(open(args.data_path, 'r')):
        conflict_info = json.loads(line)
        conflict_id = conflict_info['id']
        conflict_title = conflict_info['title']
        if conflict_id is None or conflict_title is None:
            continue

        # Collect and process the raw Wikipedia content.
        conflict_page = wikipedia.page(pageid=conflict_id)
        conflict_as_json = document_to_json(conflict_page.content, title=conflict_title)

        # Save the conflict as a json file.
        with open(os.path.join(args.save_dir, conflict_title + ".json")) as outfile:
            json.dump(conflict_as_json, outfile, sort_keys=True, indent=4)



if __name__ == "__main__":
    main()
