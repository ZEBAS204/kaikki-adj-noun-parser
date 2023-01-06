#!/usr/bin/env python

import logging
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pycountry
from bs4 import BeautifulSoup, SoupStrainer

languages_url = "https://kaikki.org/dictionary/index.html"
try:
    urllib.request.urlopen(languages_url)

except urllib.request.HTTPError as err:
    logging.critical("Cannot get document of all available languages on Kaikki")
    logging.exception(err)
    sys.exit(0)


def get_supported_languages():
    import re

    r = urllib.request.urlopen(languages_url)
    htmlContent = r.read()

    only_li_tags = SoupStrainer("li")
    soup = BeautifulSoup(htmlContent, "html.parser", parse_only=only_li_tags)

    anchors = soup.find_all("a")

    supported_languages = []
    for link in anchors:
        href = link.get("href")
        if href != "#" and "./" not in href and "combined" not in href:
            lang_name = re.sub(r"(\s?\(.+?\))", "", link.contents[0])
            lang_link = f"{languages_url.replace('index.html', '')}{href}"
            supported_languages.append(
                {
                    "name": lang_name.replace(" ", "_"),
                    "link": lang_link,
                }
            )

    return supported_languages


def file_retrieve(url, dest) -> bool:
    filename = dest.stem
    url = urllib.parse.quote(url, safe=":/", encoding="utf-8")
    max_retries = max(0, 5)

    if dest.resolve().exists():
        logging.info(f'File "{filename}" already exists. Content will be overwritten')

    logging.debug(f'Downloading "{filename}": {url}')

    for retry in range(max_retries + 1):
        if retry > 0:
            logging.debug(f"Download retries: {retry}")

            try:
                urllib.request.urlretrieve(url, filename=dest)
                # If we arrive here, the download was successful
                return True

            except urllib.error.ContentTooShortError as err:
                # This exception appeast when urlretrieve() detects that the amount of data available was less than
                # the expected amount (which is the size reported by a Content-Length header). The downloaded data
                # can still be retrieved as it is stored in the content attribute of the exception instance.
                # But, as this error is mostly likely due to a bad internet connection, we should keep retrying.
                if retry < max_retries:
                    logging.warning("Content too short: %s - will retry", url)
                    continue

                logging.warning("Max retries exceeded %s", url)
                break

            except urllib.request.HTTPError as err:
                logging.exception(err)
                logging.error("Error while retrieving from %s", url)
                break

    logging.error(f"Cannot get language set: {filename}")
    return False


def downloadLanguageSets(lang: str, dest=None):
    extension = ".kds"  # Stands for Kaikki Dictionary Set

    if dest == None:
        dest = Path("sets").resolve()
    else:
        if type(dest) is not str:
            logging.critical("The destination path expected a string")
            return
        dest = Path(dest).resolve()

    # Create folder if does not exists
    dest.mkdir(exist_ok=True, parents=True)

    countryCode = pycountry.languages.get(name=lang)
    if not countryCode:
        logging.warning("No country code found. The name will be used instead.")
        countryCode = lang.lower().replace("_", "")
    else:
        countryCode = countryCode.alpha_2
    logging.debug(f'Country code for "{lang}" is "{countryCode}"')

    # Normalize language if needed
    # Since CLI doesn't support spaced languages, underscores are treated as spaces
    lang = lang.strip().title().replace("_", " ")

    noun_dest = Path(dest / f"{countryCode}_nouns{extension}").resolve()
    adj_dest = Path(dest / f"{countryCode}_adj{extension}").resolve()

    # * Note: this files are JSON format for convenience but will fail to parse because
    # * every line inside of them corresponds to a JSON document.
    # eg. https://kaikki.org/dictionary/English/by-pos/adj/kaikki.org-dictionary-English-by-pos-adj.json
    # * The fist language is spaced
    urlLang = lang.replace(" ", "%20")
    # * Kaikki uses Pascalcase without spaces for file names
    urlFile = lang.replace(" ", "")
    noun = f"https://kaikki.org/dictionary/{urlLang}/by-pos-adj/kaikki_dot_org-dictionary-{urlFile}-by-pos-adj.json"
    adj = f"https://kaikki.org/dictionary/{urlLang}/by-pos-noun/kaikki_dot_org-dictionary-{urlFile}-by-pos-noun.json"

    nouns_success = file_retrieve(noun, noun_dest)
    adj_success = file_retrieve(adj, adj_dest)

    if nouns_success:
        logging.info(f"Successfully downloaded {lang} nouns")
    if adj_success:
        logging.info(f"Successfully downloaded {lang} adjectives")

    # Cleans up temporary files that may have been left behind by previous calls
    logging.debug("Removing temporary files from urllib...")
    urllib.request.urlcleanup()


def fetch_set(lang: str, location=None):
    if type(lang) is not str:
        raise ValueError("Language code must be a string")

    if not lang or lang.isspace():
        raise ValueError("Language code must be provided")

    if location is not None:
        if type(location) is not str:
            raise ValueError("Location must be a string")

        if location.isspace():
            raise ValueError("Location can not be empty")

    logging.debug(f"Fetching {lang}...")
    downloadLanguageSets(lang, location)

    logging.info("Finished fetching language sets")
