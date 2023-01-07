import logging
import re

from wordfreq import tokenize, word_frequency

__blacklisted_tags__ = [
    "abbreviation",
    "initialism",
    "slang",
    "vulgar",
    "obsolete",
]

"""
* Basic list of blacklisted characters to easily filter any
* punctuation characters
"""
# We use `string.punctuation` to blacklist any ASCII characters
# which are considered punctuation characters (in the C locale)
__blacklisted_characters__ = "°!¡\"#$%&'()*+,./:;<=>¿?@[\\]^_`{|}~"

"""
* The more completed blacklist of characters
* Use the above before this one to improve performance
Regex expression test strings: https://regex101.com/r/nMBju6/1

Check all Unicode characters at:
    - https://unicode-table.com/en/blocks/
    - https://unicode.org/Public/UNIDATA/NamesList.txt

Note: This does not filter zalgo
Note2: For the sake of simplicity, some character class contains duplicates
"""
__blacklisted_characters__re = re.compile(
    r"""
    # Currency Symbols
    [\u20A0-\u20CF]

    #! [\u2100-\u214F] Letterlike Symbols
    #! Some of the letterlike symbols are intended to complete the set of mathematical alphanumeric symbols starting at 1D400
    #! But will remove any: k å ω

    # Number Forms
    # Arrows
    # Mathematical Operators
    # Miscellaneous Technical
    # Control Pictures
    # Optical Character Recognition
    # Enclosed Alphanumerics
    # Box Drawing
    # Block Elements
    # Geometric Shapes
    # Miscellaneous Symbols
    # Dingbats
    # Miscellaneous Mathematical Symbols-A
    # Supplemental Arrows-A
    # Braille Patterns
    # Supplemental Arrows-B
    # Miscellaneous Mathematical Symbols-B
    # Supplemental Mathematical Operators
    # Miscellaneous Symbols and Arrows
    | [\u2150-\u2BFF]

    # Common Indic Number Forms
    | [\uA830-\uA83F]

    # Variation Selectors
    # Vertical Forms
    | [\uFE00-\uFE1F]

    # Combining Half Marks
    | [\uFE20-\uFE2F]

    # Small Form Variants
    | [\uFE50-\uFE6F]

    # Halfwidth and Fullwidth Forms
    # Specials
    | [\uFF00-\uFFFF]

    # Aegean Numbers
    # Ancient Greek Numbers
    | [\U00010100-\U0001018F]

    # Coptic Epact Numbers
    | [\u102E-\u102F]

    # Rumi Numeral Symbols
    | [\u10E6-\u10E7]

    # Sinhala Archaic Numbers
    | [\u111E-\u111F]

    # Cuneiform Numbers and Punctuation
    | [\u1240-\u1247]

    # Shorthand Format Controls
    # Byzantine Musical Symbols
    # Musical Symbols
    # Ancient Greek Musical Notation
    # Mayan Numerals
    | [\u1BCA-\u1D2F]

    # Counting Rod Numerals
    # Mathematical Alphanumeric Symbols
    # Sutton SignWriting
    | [\U0001D360-\U0001DAAF]

    # Indic Siyaq Numbers
    # Ottoman Siyaq Numbers
    # Arabic Mathematical Alphabetic Symbols
    # Mahjong Tiles
    # Domino Tiles
    # Playing Cards
    # Enclosed Alphanumeric Supplement
    # Enclosed Ideographic Supplement
    # Miscellaneous Symbols and Pictographs
    # Emoticons (Emoji)
    # Ornamental Dingbats
    # Transport and Map Symbols
    # Alchemical Symbols
    # Geometric Shapes Extended
    # Supplemental Arrows-C
    # Supplemental Symbols and Pictographs
    # Chess Symbols
    # Symbols and Pictographs Extended-A
    | [\U0001EC70-\U0001FAFF]
    """,
    flags=re.IGNORECASE | re.VERBOSE | re.UNICODE,
)

__wasblacklisted__ = set()


def clear_blacklisted():
    logging.debug("Blacklist cleared!")
    __wasblacklisted__.clear()


def save_blacklisted_word(word, type="known", altOf=None):
    logging.info(f"Adding word to blacklist: {word}")
    if type == "known":
        __wasblacklisted__.add(word)
        logging.debug(f"{type}\t{word}\n")

    else:
        logging.debug(f"{type}\t{word} -> {altOf}\n")


def get_word_tags(data: dict):
    tags = set()

    # senses is always guaranteed to be, no check needed
    for sense in data["senses"]:
        if "tags" not in sense:
            continue
        for tag in sense["tags"]:
            tags.add(tag.lower())

    if "forms" in data:
        for forms in data["forms"]:
            if "tags" not in forms:
                continue
            for tag in forms["tags"]:
                tags.add(tag.lower())

    logging.debug(f"Found a total of {len(tags)} tags for the word {data['word']}")
    return tags


def is_tag_blacklisted(tags: set, word):
    # If word is spaced, then is probably a say and should be skipped
    # Instead of regex, use split as the default includes all whitespaced characters
    # Max split is set to 1 as checking multiple spaces is pointless
    if len(word.split(maxsplit=1)) > 1:
        logging.debug(f"{word} contains whitespaced character/s")
        return True

    # First check for numbers and limited blacklisted characters
    for char in word:
        if char.isdigit():
            logging.debug(f"({char}) - {word} contains a number")
            return True

        if any(c in __blacklisted_characters__ for c in char):
            logging.debug(f"({char}) - {word} contains a blacklisted character")
            return True

    # Check if contains any blacklisted tag
    if tags and any(i in tags for i in __blacklisted_tags__):
        logging.debug(f"{word} contains a blacklisted tag")
        save_blacklisted_word(word)
        return True

    # Check if was previously blacklisted
    # ! __wasblacklisted__ set size may degrade performance over time
    if word in __wasblacklisted__:
        logging.debug(f"Word was previously blacklisted: {word}")
        return True

    # Fully check if contains a blacklisted character using regex
    if bool(__blacklisted_characters__re.match(rf"{re.escape(word)}")):
        logging.debug(f"{word} contains a blacklisted unicode character!")
        save_blacklisted_word(word)
        return True

    # Check if matches any previously blacklisted word
    # ! May degrade performance over time
    for blackListedWord in __wasblacklisted__:
        if bool(re.match(rf"{re.escape(word)}", re.escape(blackListedWord))):
            logging.debug(
                f"A previously word was blacklisted:\nVariation: {word} -> blacklisted: {blackListedWord}"
            )
            save_blacklisted_word(word, "alter", blackListedWord)
            return True

    # * Not a blacklisted word
    return False


def is_word_used(
    word: str,
    lang: str,
    wordlist: str = "best",
    minimum: float = 0.0,
) -> bool:
    """
    `is_word_used` returns the frequency of a word in a language

    :param word: str = The word you want to check the frequency of
    :type word: str
    :param lang: The language you want to get the frequency for
    :type lang: str
    :param wordlist: str = "best", defaults to best
    :type wordlist: str (optional)
    :param minimum: The minimum frequency of the word in the wordlist
    :type minimum: float
    :return: A bool
    """

    # As some of the words may be hyphenated words,
    # we separate and reject any words that tokenize to more than two words
    if len(tokenize(word, lang)) > 2:
        return False

    frequency = word_frequency(word, lang, wordlist, minimum)
    is_used = frequency > 5.62e-06  # 0.00000562
    return is_used
