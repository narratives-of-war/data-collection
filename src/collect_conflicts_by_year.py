
import os
import sys
from urllib.parse import unquote


from war_wikipedia import collect_conflicts_from_year, collect_war_content_by_id, collect_war_content_by_title

"""
TODO - collect the 5000 ish things that Wikipedia considers a conflict, supplement with what wikipedia
       believes is a battle, what it thinks is a war, and collect all tangential 'categories'.
"""


def main():
    if len(sys.argv) < 3:
        print("Usage: python collect_conflicts_by_year.py <Categories> <output_dir>")
        sys.exit()

    print("Collecting conflicts by year:")
    year_file = sys.argv[1]
    output_dir = sys.argv[2]

    conflicts_txt = os.path.join(output_dir, "conflicts.txt")

    if not os.path.exists(conflicts_txt):
        # For each year defined, collect all of the conflicts.
        conflict_titles = set()
        with open(year_file, 'r') as f:
            year_ids = f.readlines()
            for year_id in year_ids:
                print("  collecting conflicts in", year_id, end="")
                conflict_titles.update(collect_conflicts_from_year(year_id))

        print(len(conflict_titles), "conflicts found; Collect conflict content by wiki ID:")
        conflict_titles = set(map(unquote, conflict_titles))

        # Print to file for convenience
        with open(conflicts_txt, "w") as c:
            for conflict_title in conflict_titles:
                print(conflict_title, file=c)
    else:
        with open(conflicts_txt, "r") as c:
            conflict_titles = set(c.readlines())

    # For each battle id, collect the content and meta data
    battles_dir = os.path.join(output_dir, "conflicts")
    if not os.path.exists(battles_dir):
        os.mkdir(battles_dir)

    content_dir = os.path.join(output_dir, "content")
    meta_dir = os.path.join(output_dir, "meta")
    if not os.path.exists(content_dir) or not os.path.exists(meta_dir):
        os.mkdir(content_dir)
        os.mkdir(meta_dir)

    collection_failures = []
    tangential_conflicts = set()
    while len(conflict_titles) != 0:

        # Categories are recursive; save them and decide later whether to
        # explore them.
        conflict_title = conflict_titles.pop().strip()
        if "Category:" in conflict_title:
            print("Collecting and saving more conflicts:", conflict_title)
            more_conflicts = collect_conflicts_from_year(conflict_title)
            tangential_conflicts.update(more_conflicts)
        else:
            # Attempt to collect via ID or Titles
            file_count = 0
            print(len(conflict_titles), "left, collecting", conflict_title, "...")
            conflict_title = unquote(conflict_title)
            try:
                print("  Collecting via ID:")
                file_count = collect_war_content_by_id(conflict_title, content_dir, meta_dir)
            except:
                try:
                    print("  Collecting via Title:")
                    conflict_title = conflict_title.replace("_", " ")
                    file_count = collect_war_content_by_title(conflict_title, content_dir, meta_dir)
                except:
                    pass

            if file_count == 2:
                print("    ", conflict_title, "meta-data and content collected!")
            elif file_count == 1:
                print("      ", conflict_title, "content collected!")
            else:
                print("      collection failure")
                collection_failures.append(conflict_title)

    # Escape into actual titles
    map(unquote, tangential_conflicts)
    print("\nTangential topics:")
    map(print, tangential_conflicts)

    print("\nSaving tangential topics...\n")
    with open(os.path.join(output_dir, "tangents.txt"), "w") as tangent_file:
        for t in tangential_conflicts:
            print(t, file=tangent_file)

    print("\nCollection failures:")
    map(print, collection_failures)


if __name__ == "__main__":
    main()
