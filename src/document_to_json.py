
import os
import sys
import urllib

from war_wikipedia import collect_ids_by_era, collect_war_content_by_title


def main():
    if len(sys.argv) < 3:
        print("Usage: python collect_data_by_era.py <content_dir> <output_dir>")
        sys.exit()

    content_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for file in os.listdir(content_dir):
        with open(os.path.join(content_dir, file), "r") as f:
            print("Processing", file[:-4], "...")
            # Replace newlines and double quotes for proper JSON
            content = f.read().replace("\n", " ").replace('\"', '\\\"')
            content_json = "{\"document\":\"" + content + "\"}"
            document_json_path = os.path.join(output_dir, file[:-4] + ".jsonl")
            with open(document_json_path, "w") as document_json:
                print(content_json, file=document_json)

    print("Document JSON versions created.")


if __name__ == "__main__":
    main()
