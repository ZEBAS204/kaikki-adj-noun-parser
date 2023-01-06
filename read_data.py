import json
import logging
from pathlib import Path
from time import process_time as perfTime

from build_data import get_wordsets
from filters import clear_blacklisted, get_word_tags, is_tag_blacklisted, is_word_used

# Your sets to get the words from
word_sets_files = get_wordsets()


# * Save to file
def save_dictionary(filePath, lang, wordType, words):
    filePath.parent.mkdir(exist_ok=True, parents=True)
    with open(filePath, "w", encoding="utf-8") as f:
        # * Sort if needed
        matches = sorted(list(words), key=len)
        f.write(json.dumps(matches, ensure_ascii=False, indent=2))
        logging.info(
            f'Created "{lang}_{wordType}.json" with a total of {len(words)} {wordType}s'
        )


def handle_wordsets(lang: str, wordSet, destination=None):
    logging.debug(f"Handling language: {lang}")

    if destination is None:
        destination = Path("dict").resolve()
    else:
        # TODO: destination
        destination = Path(".")

    for wordFile in [wordSet["noun"], wordSet["adj"]]:
        # * Get current word type (noun or adj)
        wordType = [k for k, v in wordSet.items() if v == wordFile][0]
        directory = Path(wordFile).resolve()
        logging.info(f"Parsing {lang} for {wordType} in {directory}...")

        filePath = Path(destination / f"{lang}_{wordType}.json").resolve()

        if filePath.exists():
            # TODO: add ability to override existing content
            logging.info(f'File "{directory.name}" already exists.')
            continue

        with open(f"{directory}", "r", encoding="utf-8") as f:
            # * To avoid duplicated words, we need to create a set.
            # * If you will like to also check for duplicates, then replace it with an
            # * array, replace line 32 'add' with 'append' and uncomment the bottom lines.
            words = set()
            
            # * As every line is it's own object, we need to loop every line
            # * If we try to parse it with json, then an error will be raised.
            totalIgnored = 0
            for line in f:
                data = json.loads(line)
                thisWord = data["word"].lower()
                thisWordSenses = get_word_tags(data=data)

                if is_tag_blacklisted(thisWordSenses, thisWord):
                    totalIgnored += 1
                    logging.debug(f"{thisWord} is blacklisted.")
                    continue

                if is_word_used(thisWord, lang):
                    words.add(thisWord)

            logging.info(
                f"A total of {totalIgnored} words where ignored for the {lang} language"
            )
            save_dictionary(filePath, lang, wordType, words)


# Loop through all words
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.root.setLevel(logging.INFO)

    if word_sets_files is not None:
        for wordSet in word_sets_files:
            logging.debug(f"Parsing word set: {wordSet}")

            # Loop through nouns and adjectives files
            lang = wordSet["lang"]
            elapsed = perfTime()

            # Handle words sets
            handle_wordsets(lang, wordSet)
            logging.info(
                f"{lang.upper()} language took {perfTime() - elapsed} seconds to complete"
            )

            # Clear words blacklist from the language
            clear_blacklisted()
