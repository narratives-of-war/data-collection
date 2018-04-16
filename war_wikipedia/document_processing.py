

def document_to_json(title, path):

    # Wikipedia articles will have sections preceeded by
    # === Section Title ===
    # Where the number of ='s determine the section type.
    #
    # We treat sections indifferently when building the JSON:
    # sections: {
    #    "heading": heading from === Section Title ===
    #    "text": text from the section
    #


    with open(path, 'r') as f:
        lines = f.readlines()

    sections = []
    headings = []

    # All articles have an intro body of text with no header.
    current_heading = "Introduction"
    current_section = []
    for line in lines:

        # Reached a section header.
        if line.startswith("="):
            headings.append(current_heading)
            sections.append(current_section)
            current_heading = line.replace("=", "")
            current_section = []
        else:
            current_section.append(line)

    document_as_json = {
        "title": title,
        "sections": []
    }

    for i in range(len(sections)):
        current_heading = headings[i]
        current_section = sections[i]
        section_as_json = {
            "heading": current_heading.strip(),
            "text": ''.join(current_section)
        }
        document_as_json["sections"].append(section_as_json)

    return document_as_json
