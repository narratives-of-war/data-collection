import argparse
import json
import os
import shutil
import sys

from tqdm import tqdm
from urllib.parse import unquote

from war_wikipedia import *


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    project_root = os.path.abspath(os.path.realpath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)))))

    parser.add_argument("--conflicts-path", type=str,
                        help="Path to the list of conflict IDs to collect from.")
    parser.add_argument("--save-dir", type=str,
                        default=os.path.join(
                            project_root, "data"),
                        help="Directory to save content content as"
                             "text files.")
    args = parser.parse_args()

    conflict_ids = []
    print("Collecting conflict IDs from eras:")

    if not args.conflicts_path:
        try:
            if os.path.exists(args.save_dir):
                # save directory already exists, do we really want to overwrite?
                input("Directory for conflict data \'{}\' already exists. Press <Enter> "
                      "to clear, overwrite and continue , or "
                      "<Ctrl-c> to abort.".format(args.save_dir))
                shutil.rmtree(args.save_dir)
            os.makedirs(args.save_dir)
        except KeyboardInterrupt:
            print()
            sys.exit(0)

        # Collect IDs of all conflict eras in the 20th century:
        conflict_by_era_categories = collect_ids_by_category(TWENTIETH_CENTURY_CATEGORY)
        conflict_by_era_categories += collect_ids_by_category(TWENTY_FIRST_CENTURY_CATEGORY)
        print(len(conflict_by_era_categories), "conflicts eras found!")

        # Collect IDs of all conflicts from every era:
        for era_category in tqdm(conflict_by_era_categories):
            conflict_ids += collect_ids_by_category(era_category)
        print(len(conflict_ids), "conflicts found!")

        # Some pages aren't actually articles
        unfiltered_conflict_ids = conflict_ids
        conflict_ids = []
        categories = []
        for conflict_id in unfiltered_conflict_ids:
            if conflict_id.startswith("Category:"):
                categories.append(conflict_id)
            else:
                conflict_ids.append(conflict_id)

        print("Storing conflict IDs:")

        # Escape HTML chars.
        conflict_ids = list(map(unquote, conflict_ids))

        # Store them as it takes time to collect.
        conflict_ids_file = os.path.join(args.save_dir, "conflict_ids.txt")
        with open(conflict_ids_file, 'w') as f:
            for c in conflict_ids:
                print(c, file=f)
            f.close()

        # Store the categories in case they're useful.
        category_ids_file = os.path.join(args.save_dir, "category_ids.txt")
        with open(category_ids_file, 'w') as f:
            for c in categories:
                print(c, file=f)
            f.close()
    else:
        conflict_ids_file = args.conflicts_path

    with open(conflict_ids_file, 'r') as f:
        conflict_ids = f.readlines()

    # Directories for content and info boxes.
    content_dir = os.path.join(args.save_dir, "content")
    if not os.path.exists(content_dir):
        os.mkdir(content_dir)

    meta_dir = os.path.join(args.save_dir, "meta")
    if not os.path.exists(meta_dir):
        os.mkdir(meta_dir)

    conflict_ids = set(conflict_ids)  # Remove redundant entries.
    print("Collecting", len(conflict_ids),  "non-redundant conflicts:")

    try:
        for conflict_id in tqdm(conflict_ids):
            collect_content(conflict_id, content_dir, meta_dir)

        print("Data collected!")
    except KeyboardInterrupt:
        print("Collection ended early.")


if __name__ == "__main__":
    main()
