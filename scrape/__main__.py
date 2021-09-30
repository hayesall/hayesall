# Copyright 2020 Alexander L. Hayes

"""
Scrape Alexander's reading list to pull what he is currently reading.

TODO
----

I wrote everything in the main module, these things happen when we work too
quickly and hope things will work out.

Usage Instructions
------------------

.. code-block:: bash

    python -m scrape --help

Recommended
-----------

Start with a "dry run" where all results are printed out to the console:

.. code-block:: bash

    python -m scrape -d

License
-------

Copyright 2020 Alexander L. Hayes
MIT License
"""

import argparse
import sys
from bs4 import BeautifulSoup
from liquid import Liquid
import requests

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-l", "--log", action="store_true", help="Log steps for debugging.")
PARSER.add_argument(
    "-d",
    "--dry-run",
    action="store_true",
    help="Skip writing files, print all results.",
)
ARGS = PARSER.parse_args()

LOG = ARGS.log
URL = "https://openlibrary.org/people/hayesall/books/currently-reading"

# Soup the page
html_page = requests.get(URL)
soup = BeautifulSoup(html_page.text, "html.parser")

currently_reading = soup.find("li", class_="searchResultItem")

# The cover image
try:
    _cover = "https:" + currently_reading.a.img.get("src")
except AttributeError:
    print("This probably means the 'Currently Reading' list is empty.")
    sys.exit(0)
if _cover == "https:/images/icons/avatar_book-sm.png":
    # TODO(hayesall): This handles an error where the cover is not found.
    _cover = "https://openlibrary.org/images/icons/avatar_book-sm.png"
if LOG:
    print("Cover Image:", _cover)

if not ARGS.dry_run:
    # Download the cover image so I don't hit their API to hard.
    with open("static/images/cover.jpg", "wb") as _fh:
        response = requests.get(_cover, stream=True)
        if not response.ok:
            print(response)
        for block in response.iter_content(1024):
            if not block:
                break
            _fh.write(block)

# The title
_title = currently_reading.h3.a.text
if LOG:
    print("Title:", _title)

# The author
_author = currently_reading.find("span", class_="bookauthor").a.text
if LOG:
    print("Author:", _author)

liq = Liquid("static/README-template.md")
ret = liq.render(book_name=_title, book_author=_author,)

if ARGS.dry_run:
    print(ret)
else:
    with open("README.md", "w") as _fh:
        _fh.write(ret)
