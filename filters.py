import re
import logging
from wordfreq import word_frequency, tokenize


__whitelist__ = [
    "singular",
    "plural",
    "feminine",
    "masculine",
    "relational",
]

__blacklisted_tags__ = ["abbreviation", "slang", "vulgar"]

__wasblacklisted__ = set()


def clear_blacklisted():
    logging.debug("Blacklisted word list cleared!")
    __wasblacklisted__.clear()


def saveBlackListedWord(word, type="known"):
    logging.info(f"Adding word to blacklist: {word}")
    __wasblacklisted__.add(word)

    # * Temp
    with open("blacklist.txt", "a", encoding="utf-8") as f:
        f.write(f"{type}\t{word}\n")


def is_tag_blacklisted(senses, word):
    word = word.lower()

    if word in __wasblacklisted__:
        print(f"Word was previously blacklisted: {word}")
        return True

    for blackListedWord in __wasblacklisted__:
        if bool(re.match(rf"{re.escape(word)}", re.escape(blackListedWord))):
            print(
                f"A previously word was blacklisted:\nVariation: {word} -> blacklisted: {blackListedWord}"
            )
            saveBlackListedWord(word, "alter")
            return True

    tags = set()

    # * Add all tags found into the set
    for sense in senses:
        if not "tags" in sense:
            continue
        for tag in sense["tags"]:
            tags.add(tag.lower())

    if len(tags) == 0:
        return False

    isBlackListed = any(i in tags for i in __blacklisted_tags__)

    if isBlackListed:
        saveBlackListedWord(word)

    return isBlackListed


def is_word_used(
    word: str,
    lang: str,
    wordlist: str = "best",
    minimum: float = 0.0,
) -> bool:
    """
    `get_word_frenquency` returns the frequency of a word in a language

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

    # * If the provided word is made by more than just a single word,
    # * then is probably a say and should be skipped.
    if len(tokenize(word, lang)) != 1:
        return False

    frequency = word_frequency(word, lang, wordlist, minimum)
    is_used = frequency > 5.62e-06  # 0.00000562
    return is_used
