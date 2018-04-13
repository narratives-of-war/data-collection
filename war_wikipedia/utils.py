import os
import re
from urllib.parse import quote
import requests

from bs4 import BeautifulSoup
import wikipedia

TWENTIETH_CENTURY_CATEGORY = "Category:20th-century_conflicts_by_year"
TWENTY_FIRST_CENTURY_CATEGORY = "Category:21st-century_conflicts_by_year"


def collect_ids_by_category(century_category):
    """
    Wikipedia has conflict categories spanning from 1901 to present day:
    https://en.wikipedia.org/wiki/Category:20th-century_conflicts_by_year
    https://en.wikipedia.org/wiki/Category:21st-century_conflicts_by_year

    The web pages themselves contain links to categories of the form
    Category:Conflicts_in_XXXX for years 1901 to 2018.

    This method collects each Category:Conflict_in_XXXX for the 20th and
    21st centuries.

    :return A list of Wikipedia IDs, which could be more categories themselves!
    """

    # Collect the html
    url = "https://en.wikipedia.org/wiki/" + quote(century_category.strip())
    response = requests.get(url)
    page_soup = BeautifulSoup(response.content, "html5lib")

    # Each 'mw-cateory' in a category/subcategory page contains the
    # list of conflicts by year.
    #
    # Each category page has a single mw-category or an ID of mw-pages
    # Ignore category pages that don't include either
    subcategories = page_soup.findAll("div", attrs={"class": "mw-category"})
    conflicts_from_century = []
    if len(subcategories) == 0:
        subcategories = page_soup.findAll("div", attrs={"id": "mw-pages"})

    # Collect the conflict by year IDs.
    for subcategory in subcategories:
        for a in subcategory.findAll("a", href=True):
            # href has the form /wiki/Category:XXXXXXXX
            conflicts_from_century.append(a['href'].split("/")[-1])

    return conflicts_from_century


def collect_content(conflict, content_dir, meta_dir):
    """
    Given a war id, creates:
    - A text file containing belligerents and casualties
    - A text file containing raw wikipedia content
    :param conflict: string
        The unique string found after /wiki/ on wikipedia articles.
    :param content_dir: path
        The directory to store the content file
    :param meta_dir: path
        The directory to store the conflict statistics (casualties,
        belligerents, etc.) if present.
    :param type: If "id", assumes 'conflict' is the conflict page's ID.
        If 'title', assumes it is a title instead.
    :return: 2 if both the content file and meta file were created, 1 if only
        the content file. Returns None if the conflict could not be collected.
    """
    war_page = None

    try:
        war_page = wikipedia.page(conflict)
    except:
        # Titles don't have underscores or hyphens, they use spaces..
        title = re.sub(r'[-_]', ' ', conflict)
        war_page = wikipedia.page(title=title)

    if war_page == None:
        return None

    content_file = open(os.path.join(content_dir, conflict + ".txt"), "w")
    meta_file = open(os.path.join(meta_dir, conflict + ".txt"), "w")

    war_soup = BeautifulSoup(war_page.html(), "lxml")
    print(war_page.content, file=content_file)
    meta_data = info_box(war_soup)
    if meta_data is not None:
        print(meta_data, file=meta_file)
        return 2

    return 1


def info_box(soup):
    """
    Given the Wikipedia soup the war, returns the raw text of the
    informational 'vevent' box.
    :param soup: A beautiful soup object containing the conflict article.
    :return A string containing all fields of the info box.
    """

    # Extract HTML and search for 'vevent' box
    table = soup.find("table", attrs={"class": "vevent"})

    if table is None:  # Not all events have an info box
        return None

    # Exclude HTML tags
    remove_tags = re.compile('<.*?>')
    clean = re.sub(remove_tags, '', table.prettify())

    def informative(s):
        # Filters out blank lines and references that use []
        # Also filters out lines consisting of only commas and hyphens
        # as well as extraneous details found in ().
        return s.strip() and re.match(r'[^\-c()\[\],]', s.strip())

    clean = os.linesep.join([s for s in clean.splitlines() if informative(s)])

    return clean


def war_id_collection_by_era(era_id):
    """
    Given a 'List of Wars by XYZ' wikipedia page ID, collects
    all of the war wiki IDs.
    :param era_id: Wikipedia ID of list of wars for an era
        Example: https://en.wikipedia.org/wiki/List_of_wars_1900-44 has
        ID List_of_wars_1900-44
    :return A list of the the war IDs extracted.
    """
    page = wikipedia.page(era_id)
    page_soup = BeautifulSoup(page.html(), "lxml")

    # Each 'wikitable' in a 'List of Wars' page contains the list of
    # wars and belligerents
    tables = page_soup.findAll("table", attrs={"class": "wikitable"})

    # For each table, collect the war IDs from the third column.
    war_titles = []
    for table in tables:
        for row in table.findAll('tr'):
            entries = row.findAll('td')
            if len(entries) > 0:
                war_datum = entries[2]
                war_title = war_datum.find("a", title=True)['title']

                # Exclude defunct pages
                if "page does not exist" not in war_title:
                    war_titles.append(war_title)

    return war_titles
