import argparse
import json
import os

from tqdm import tqdm

from war_wikipedia import document_to_json


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    project_root = os.path.abspath(os.path.realpath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)))))

    parser.add_argument("--data-path", type=str,
                        default=os.path.join(
                            project_root, "data"),
                        help="Path to data directory to finalize.")
    args = parser.parse_args()

    print("Collecting Conflict Wikipedia articles from the data directory:")
    content_dir = os.path.join(args.data_path, "content")

    # Output directory.
    json_dir = os.path.join(args.data_path, "JSON")
    if not os.path.exists(json_dir):
        os.mkdir(json_dir)

    # Create the JSON analogue of every text file.
    print("Making Conflict JSON files from documents:")
    documents = os.listdir(os.path.join(args.data_path, "content"))
    for document in tqdm(documents):
        file_prefix = document.split(".")[0].strip()
        conflict_name = file_prefix.replace("_", " ")
        document_path = os.path.join(content_dir, document)
        conflict_as_json = document_to_json(conflict_name, document_path)
        conflict_json_file = os.path.join(json_dir, file_prefix + ".json")

        with open(conflict_json_file, 'w') as outfile:
            json.dump(conflict_as_json, outfile, indent=4, sort_keys=True)

    print("Data converted to JSON!")


if __name__ == "__main__":
    main()
