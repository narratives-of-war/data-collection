""" Conversion from raw Wikipedia to JSON.
"""

def document_to_json(content, title=None):
    """
    Given the title and full path to the raw Wikipedia content as a result of
    Wikipedia.page(pageid=...), returns a JSON-formatted version of the page.

    Wikipedia articles will have sections preceeded by '=== Section Title ==='
    where the number of ='s determine the section type.

    We treat sections indifferently when building the JSON, which
    results in
    {
        "title":
        "sections": [
         { "heading": (heading from === Section Title ===)
           "text": (text from the section) }
                   ...
        ]
    }

    Parameters
    -----------
    path : ``str`` The full path to the raw Wikipedia content.
    title : ``str``, (defaule=``None``) The name of the conflict to be preserved in the JSON.
    """
    lines = content.split('\n')
    sections = []
    headings = []

    # All articles have an intro body of text with no header.
    current_heading = "Introduction"
    current_section = []
    for line in lines:
        if line.startswith("="):  # Reached a section header.
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

    for i, current_section in enumerate(sections):
        current_heading = headings[i]
        section_as_json = {
                "heading": current_heading.strip(),
                "text": ''.join(current_section)
        }
        document_as_json["sections"].append(section_as_json)

    return document_as_json
