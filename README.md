
## Requirements

- [Kaikki dictionary](https://kaikki.org/dictionary/) ???
  [wiktextract](https://github.com/tatuylonen/wiktextract) can be used to generate the same dictionaries if you wish so.
- [Wordfreq's word frequencies](https://github.com/rspeer/wordfreq/)
- [Bad words list](https://github.com/hughsie/badwords)

## How does it work

Before we start, **"Word Sets" refer to nouns and adjectives of a language**.
In this case, mostly used when talking about the JSON files that contain the nouns and adjectives separately.

1. Get the word sets of the desired language/s (see [Getting the word sets of a language](#getting_the_word_sets_of_a_language))
2. Remove duplicates.
3. Remove spaced (most likely says) words.
4. Remove blacklisted tags if necessary.
5. Alphabetically sort words if necessary.
6. Use Wordfreq's library to filter the most common words of the language.
7. Extract all filtered words into a JSON file as an array of words.

## Getting the word sets of a language

### Automated method

To download the word sets of your desired languages to parse, inside the folder `utils` you can use the function `fetch_set` inside `fetch_sets.py` script to automatically download and store them (by default, the download directory is `./sets`) from the official website.

Or use it directly from the console with the CLI command:

> $ cd utils
> $ py CLI.py --lang=Spanish English Deutch de --location sets

For more information use the `--help` command.

See all supported languages [here -](https://kaikki.org/dictionary).

### Manual method

To simplify the scope of the tool, you will have to manually download your desired language's "Senses with part-of-speech" for the Nouns and Adjectives. To do that and simplify:

1. On the ["List of kaikki.org machine-readable dictionaries"](https://kaikki.org/dictionary/), select the desired langauge/s from the "Available languages" list.
2. Inside the language's dictionaries, browse inside the "Word sense lists" for the "Senses with part-of-speech Noun" and "Senses with part-of-speech Adjectives".
3. Inside of them, under the list of all words senses, you will see a "Download JSON data for these senses (xx.xMB)". Download it.
4. Rename the noun file to `[lang]_noun.json` and save it inside the `sets` folder.
5. Rename the adjectives file to `[lang]_adj.json` and save it inside the `sets` folder.

To make it easier to understand, for example, I will go step by step to manually download the word sets for the English language:

1. Go to the ["List of kaikki.org machine-readable dictionaries"](https://kaikki.org/dictionary/) and select ["English (1397862 senses)"](https://kaikki.org/dictionary/English/index.html).
2. Inside the "Word sense lists", I download the JSON data for all the senses from the ["Senses with part-of-speech Noun (778087)"](https://kaikki.org/dictionary/English/pos-noun.html) and ["Senses with part-of-speech Adjective (187458)"](https://kaikki.org/dictionary/English/pos-adj.html).
3. The nouns JSON file ([direct download](https://kaikki.org/dictionary/English/by-pos/noun/kaikki.org-dictionary-English-by-pos-noun.json)) gets renamed to `en_noun.json` and the adjectives ([direct download](https://kaikki.org/dictionary/English/by-pos/adj/kaikki.org-dictionary-English-by-pos-adj.json)) to `en_adj.json`.
4. After that, you manually move those two files inside the root of the directory `sets`.
5. Run the script or do whatever you wish to.

## Known issues

- Cursed/bad words are not filtered.
- Will not differentiate between American and British English.
- Non-words/special words cannot be filtered (eg. 1st 1°)
- Sometimes single letters can not be filtered as they "mean" something (eg. a, letter A, b)
- Some words are wrongly categorized (eg. a noun that is a suffix)
- Filtering removes any spaced words.
- May not work properly on syllabary-based languages.
- Not tested with "Dictionaries for historical languages".
