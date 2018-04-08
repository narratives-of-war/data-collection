
import os
import re
from urllib.parse import quote
import urllib3

from bs4 import BeautifulSoup
import wikipedia


def collect_ids_by_era(era_id):
    """ Given a 'List of Wars by XYZ' wikipedia page ID, collects
        all of the war wiki IDs.
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


def collect_conflicts_from_year(category):
    """ Given a 'conflict by century' category wikipedia page ID, collects
        all of the conflict wiki IDs.
    """

    # Collect the html
    http = urllib3.PoolManager()
    url = "https://en.wikipedia.org/wiki/" + quote(category.strip())
    page = http.request('GET', url)
    page_soup = BeautifulSoup(page.data, "html5lib")

    # Each 'mw-cateory' in a category/subcategory page contains the
    # list of conflicts by year.
    #
    # Each category page has a single mw-category or an ID of mw-pages
    # Ignore category pages that don't include either
    subcategories = page_soup.findAll("div", attrs={"class": "mw-category"})
    conflicts_from_year = []
    if len(subcategories) == 0:
        subcategories = page_soup.findAll("div", attrs={"id": "mw-pages"})

    # Collect the conflict by year IDs.
    for subcategory in subcategories:
        for a in subcategory.findAll("a", href=True):
            # href has the form /wiki/Category:XXXXXXXX
            conflicts_from_year.append(a['href'].split("/")[-1])

    return conflicts_from_year


def collect_war_content_by_title(war_title, content_dir, meta_dir):
    """ Given a war id, creates:
        - A text file containing belligerents and casualties
        - A text file containing raw wikipedia content
    """
    war_page = wikipedia.page(title=war_title)
    war_file = war_title.replace(" ", "_")
    content_file = open(os.path.join(content_dir, war_file + ".txt"), "w")
    meta_file = open(os.path.join(meta_dir, war_file + ".txt"), "w")
    war_soup = BeautifulSoup(war_page.html(), "lxml")
    print(war_page.content, file=content_file)
    meta_data = info_box(war_soup)
    if meta_data is not None:
        print(meta_data, file=meta_file)
        return 2

    return 1


def collect_war_content_by_id(war_id, content_dir, meta_dir):
    """ Given a war id, creates:
        - A text file containing belligerents and casualties
        - A text file containing raw wikipedia content
    """
    war_page = wikipedia.page(war_id)
    content_file = open(os.path.join(content_dir, war_id + ".txt"), "w")
    meta_file = open(os.path.join(meta_dir, war_id + ".txt"), "w")
    war_soup = BeautifulSoup(war_page.html(), "lxml")
    print(war_page.content, file=content_file)
    meta_data = info_box(war_soup)
    if meta_data is not None:
        print(meta_data, file=meta_file)
        return 2

    return 1


def info_box(soup):
    """ Given the Wikipedia soup the war, returns the raw text
        of the informational 'vevent' box. """

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
