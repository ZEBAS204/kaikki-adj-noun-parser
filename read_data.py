import json
import logging
from pathlib import Path
from time import process_time as perfTime

from filters import is_word_used, is_tag_blacklisted, clear_blacklisted
from build_data import get_wordsets


# Your sets to get the words from
word_sets_files = get_wordsets()


def handle_wordsets(lang: str, wordFile, destination=None):
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
        print(f"Parsing {lang} for {wordType} in {directory}...")

        if directory.exists():
            print(
                f'File "{directory.name}" already exists. Content will be overwritten'
            )

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
                thisWord = data["word"]
                thisWordSenses = data["senses"]
                # logging.debug(json.dumps(data['word'], indent=2, sort_keys=True))

                if not is_tag_blacklisted(senses=thisWordSenses, word=thisWord):
                    if is_word_used(thisWord, lang):
                        # logging.debug(f'\x1b[6;30;42mIs "{thisWord}" used? TRUE\x1b[0m')
                        words.add(data["word"])
                else:
                    totalIgnored += 1
                    logging.debug(f"{thisWord} is blacklisted.")

            print(
                f"A total of {totalIgnored} words where ignored for the {lang} language"
            )

            # * Save to file
            filePath = Path(destination / f"{lang}_{wordType}.json").resolve()
            with open(filePath, "w", encoding="utf-8") as f:

                # * Sort if needed
                matches = sorted(list(words), key=len)
                f.write(json.dumps(matches, ensure_ascii=False, indent=2))
                print(
                    f'Created "{lang}_{wordType}.json" with a total of {len(words)} {wordType}s'
                )

            # Duplication check
            #! logging.debug(sorted(words))
            #! logging.debug(f"Total {wordType}s: {len(words)}")

            """
            # Check for repeated words in list
            dupWords = set(words)
            contains_duplicates = len(words) != len(dupWords)

            # Count and print duplicate words
            if contains_duplicates:
                import collections

                logging.debug(
                    f"Duplicates found!\nTotal: {len(words)} || Duplicates: {len(words) - len(dupWords)}"
                )
                logging.debug(
                    [
                        item
                        for item, count in collections.Counter(words).items()
                        if count > 1
                    ]
                )
            """


# Loop through all words
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)  #!set to DEBUG

    if not word_sets_files is None:
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
