# Kaikki Adjectives & Nouns Parser

This tool is intended to be used to create a set of dictionaries composed of two files, nouns and adjectives in JSON format.

## Installation

```console
# Clone the repo
$ git clone https://github.com/ZEBAS204/kaikki-adj-noun-parser

# Change working directory
$ cd kaikki-adj-noun-parser

# (optional) Use virtual environment
$ python3 -m pip install virtualenv
$ python3 -m venv venv
$ source env/bin/activate

# Install the requirements
$ python3 -m pip install -r requirements.txt
```

## Usage

```console
# After downloading the wordsets (.kds), run the
# build_data script to generate the wordsets.json
$ python3 build_data.py

# Now, you can parse the sets:
$ python3 parse_data.py
```

### Requirements

- [Kaikki dictionary](https://kaikki.org/dictionary/) ([Wiktextract](https://github.com/tatuylonen/wiktextract) can be used to generate the same dictionaries if you wish so).
- [Wordfreq](https://github.com/rspeer/wordfreq/) (used to tokenize words)

> **Note**
> Some languages, like Japanese, need additional dependencies to be downloaded. Please check Wordfreq's Additional CJK installations.

If you want to use the CLI, some additional dependencies are needed:

- [Pycountry](https://github.com/flyingcircusio/pycountry) (used to get the country code of languages)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) (used to parse Kaikki's web page for all available dictionaries)

## How does it work

Before we start, **"Word Sets" refer to nouns and adjectives of a language**.
In this case, mostly used when talking about the JSON files that contain the nouns and adjectives separately.

1. Get the word sets of the desired language/s (see [Getting the word sets of a language](#getting-the-word-sets-of-a-language))
2. Remove duplicates
3. Remove spaced words (most likely sayings)
4. Remove words with blacklisted tags
5. Remove words with blacklisted characters
6. Use Wordfreq to tokenize and remove any hyphened word with more than two hyphens
7. Extract all filtered words into a JSON file as an array of words
8. Sort words by length

## Getting the word sets of a language

### Automated method

To download the word sets of your desired languages to parse, inside the folder `utils` you can use the function `fetch_set` inside `fetch_sets.py` script to automatically download and store them (by default, the download directory is `./sets`) from the official website.

Or use it directly from the console with the CLI command (example):

```console
$ python3 utils/CLI.py --lang=spanish english german --location sets
Successfully downloaded en nouns
Successfully downloaded en adjectives
Successfully downloaded de nouns
Successfully downloaded de adjectives
```

For more information use the `--help` command.

See all supported languages [here](https://kaikki.org/dictionary) or use the CLI:

```console
$ python3 utils/CLI.py [-s | --supported-languages]
Supported Languages:
* English
* Latin
* Spanish
* Italian
...
```

### Manual method

To simplify the scope of the tool, you will have to manually download your desired language's "Senses with part-of-speech" for the Nouns and Adjectives. To do that and simplify:

1. On the ["List of kaikki.org machine-readable dictionaries"](https://kaikki.org/dictionary/), select the desired langauge/s from the "Available languages" list.
2. Inside the language's dictionaries, browse inside the "Word sense lists" for the "Senses with part-of-speech Noun" and "Senses with part-of-speech Adjectives".
3. Inside of them, under the list of all words senses, you will see a "Download JSON data for these senses (xx.xMB)". Download it.
4. Rename the noun file to `[lang]_noun.kds` and save it inside the `sets` folder.
5. Rename the adjectives file to `[lang]_adj.kds` and save it inside the `sets` folder.

(The extension `.kds` stands for Kaikki Dictionary Set and it should be treated as a JSON file)

To make it easier to understand, for example, I will go step by step to manually download the word sets for the English language:

1. Go to the ["List of kaikki.org machine-readable dictionaries"](https://kaikki.org/dictionary/) and select ["English (1397862 senses)"](https://kaikki.org/dictionary/English/index.html).
2. Inside the "Word sense lists", I download the JSON data for all the senses from the ["Senses with part-of-speech Noun (778087)"](https://kaikki.org/dictionary/English/pos-noun.html) and ["Senses with part-of-speech Adjective (187458)"](https://kaikki.org/dictionary/English/pos-adj.html).
3. The nouns JSON file gets renamed to `en_noun.kds` and the adjectives to `en_adj.kds`.
4. After that, you manually move those two files inside the root of the directory `sets`.
5. Run the script or do whatever you wish to.

## Known issues

- Cursed/bad words are not filtered correctly
  (to get around this issue, you can use "[Bad words list](https://github.com/hughsie/badwords)" or "[List of Dirty, Naughty, Obscene, and Otherwise Bad Words](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/)" to later filter it)
- Does not differentiate dialects (e.g. American and British English)
- Sometimes single letters can not be filtered as they "mean" something (eg. the meaning of "a" is "letter A")
- Some words are wrongly categorized (eg. a noun that is a suffix or a verb)
- Filtering removes any spaced words
- Filtering removes any word with not commonly used Unicode symbols and was not tested with all languages, you might need to tweak it
- Filtering is highly dependent on tags (no tags for a word, filtering just allows that word)
- Filtering removes any [hyphenated word](https://en.wikipedia.org/wiki/Syllabification) with more than two hyphens (and also causes the next issue).
- May not work properly on [syllabary-based](https://en.wikipedia.org/wiki/Syllabary) languages
- Not tested with "Dictionaries for historical languages"

## License

This project is licensed under the MIT license (MIT). But as this project uses content extracted using [Wiktextract](https://github.com/tatuylonen/wiktextract) from the [Wikimedia Foundation](https://www.wikimedia.org), may differ on licenses. See the [LICENSE](/LICENSE) file for more details.
