import argparse
import json
import os
import shutil
import sys

from tqdm import tqdm

from war_wikipedia import *


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    project_root = os.path.abspath(os.path.realpath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)))))

    parser.add_argument("--eras-path", type=str,
                        help="Path to the list of eras IDs to collect from.")
    parser.add_argument("--save-dir", type=str,
                        default=os.path.join(
                            project_root, "data"),
                        help="Directory to save content content as"
                             "text files.")
    args = parser.parse_args()


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


    conflict_ids = []
    print("Collecting conflict IDs from eras:")

    conflict_ids_file = os.path.join(args.save_dir, "conflict_ids.txt")
    if not os.path.exists(conflict_ids_file):

        # Collect IDs of all conflict eras in the 20th century:
        conflict_by_era_categories = collect_ids_by_category(TWENTIETH_CENTURY_CATEGORY)
        conflict_by_era_categories += collect_ids_by_category(TWENTY_FIRST_CENTURY_CATEGORY)
        print(len(conflict_by_era_categories), "conflicts eras found!")

        # Collect IDs of all conflicts from every era:
        for era_category in tqdm(conflict_by_era_categories):
            conflict_ids += collect_ids_by_category(era_category)
        print(len(conflict_ids), "conflicts found!")
        print("Storing conflict IDs:")

        # Store them as it takes time to collect.
        with open(conflict_ids_file, 'w') as f:
            for c in conflict_ids:
                print(c, file=f)
            f.close()
    else:
        print("Cached conflict ids detected; collecting now:")
        with open(conflict_ids_file, 'r') as f:
            conflict_ids = f.readlines()
            conflict_ids = list(map(quote, conflict_ids))

    print("Collecting", len(conflict_ids),  "conflicts:")


if __name__ == "__main__":
    main()
