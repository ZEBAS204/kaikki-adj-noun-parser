import json
import logging
from pathlib import Path
from time import process_time as perfTime

from build_data import get_wordsets
from filters import clear_blacklisted, is_tag_blacklisted, is_word_used

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


# *  Flag to handle interruptions
__INTERRUPTED__ = False


def handle_wordsets(lang: str, wordSet, destination=None):
    global __INTERRUPTED__
    logging.debug(f"Handling language: {lang}")

    if destination is None:
        destination = Path("dict").resolve()
    else:
        # TODO: destination
        destination = Path(".")

    for wordFile in [wordSet["noun"], wordSet["adj"]]:
        if __INTERRUPTED__:
            break

        # * Get current word type (noun or adj)
        wordType = [k for k, v in wordSet.items() if v == wordFile][0]
        directory = Path(wordFile).resolve()
        logging.info(f"Parsing {lang} for {wordType} in {directory}...")

        filePath = Path(destination / f"{lang}_{wordType}.json").resolve()

        if filePath.exists():
            # TODO: add ability to override existing content
            logging.info(f'File "{directory.name}" already exists.')
            continue

        if not directory.exists():
            logging.error(f'File "{directory.name}" does not exists in directory')
            continue

        with open(f"{directory}", "r", encoding="utf-8") as f:
            # * To avoid duplicated words, we need to create a set.
            # * If you will like to also check for duplicates, then replace it with an
            # * array, replace line 32 'add' with 'append' and uncomment the bottom lines.
            words = set()
            try:
                # * As every line is it's own object, we need to loop every line
                # * If we try to parse it with json, then an error will be raised.
                totalIgnored = 0
                for line_number, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        logging.error(
                            f"Error parsing {directory.name} at line {line_number}"
                        )
                        continue
                    thisWord = data["word"].lower()

                    if is_tag_blacklisted(data, thisWord):
                        totalIgnored += 1
                        logging.debug(f"{thisWord} is blacklisted.")
                        continue

                    if is_word_used(thisWord, lang):
                        words.add(thisWord)

                logging.info(
                    f"A total of {totalIgnored} words where ignored for the {lang} language"
                )

            # Prevent abrupt interruption and
            # allow to save any processed words
            except KeyboardInterrupt:
                __INTERRUPTED__ = True
            finally:
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
