
import os
import sys
import urllib

from war_wikipedia import collect_ids_by_era, collect_war_content_by_title


def main():
    if len(sys.argv) < 3:
        print("Usage: python collect_data_by_era.py <eras> <output_dir>")
        sys.exit()

    print("Collecting wars by era:")
    era_file = sys.argv[1]
    output_dir = sys.argv[2]

    # For each era defined, collect all of the wars.
    war_titles = set()
    with open(era_file, 'r') as f:
        era_ids = f.readlines()
        for era_id in era_ids:
            print("  collecting wars in", era_id, end="")
            war_titles.update(collect_ids_by_era(era_id))

    print(len(war_titles), "wars found; Collect war content by wiki ID:")

    # For each war id, collect the content and meta data
    content_dir = os.path.join(output_dir, "content")
    meta_dir = os.path.join(output_dir, "meta")
    if not os.path.exists(content_dir) or not os.path.exists(meta_dir):
        os.mkdir(content_dir)
        os.mkdir(meta_dir)

    for war_title in war_titles:
        print("  ", "collecting", war_title, "...")
        file_count = collect_war_content_by_title(war_title, content_dir, meta_dir)
        if file_count == 2:
            print("    ", war_title, "meta-data and content collected!")
        else:
            print("      ", war_title, "content collected!")


if __name__ == "__main__":
    main()
