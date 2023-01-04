#!/usr/bin/env python

import argparse
import logging
import multiprocessing
import sys

from fetch_sets import fetch_set, get_supported_languages

# New parser
parser = argparse.ArgumentParser(
    add_help=False,  # We need to disable it to add arguments groups. It's added later
    description="Fetch a language or multiple languages from the command line",
    epilog="""Usage example:
      * Single language:
        fetch_sets.py -lang english

      * Multiple languages:
        fetch_sets.py -lang English Spanish --loc ../my_new_folder
        fetch_sets.py -lang english middle_english ./sets_new


      See all supported languages here:
        https://kaikki.org/dictionary
    """,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

# Create a help group for the formater to group optional
# and required arguments when calling the help function
required = parser.add_argument_group("Required arguments:")
optional = parser.add_argument_group("Optional arguments:")

# Add back help command
optional.add_argument(
    "-h",
    "--help",
    action="help",
    default=argparse.SUPPRESS,
    help="Show this help message and exit",
)


# Little trick to bypass the required attribute error
class langAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        print("Supported Languages:")
        for lang in get_supported_languages():
            print(f"* {lang['name']}")
        # To avoid the required arguments error, we immediately exit
        sys.exit(0)


optional.add_argument(
    "-s",
    "--supported-languages",
    nargs="?",
    action=langAction,
    help="Show all supported languages in the dictionary",
)

# This is the correct way to handle accepting multiple arguments.
# '+' == 1 or more.
# '*' == 0 or more.
# '?' == 0 or 1.
required.add_argument(
    "--language",
    "-lang",
    nargs="+",
    type=str,
    required=True,
    dest="languages",
    help="Language/s code names (separated with spaces)",
)
optional.add_argument(
    "--destination",
    "-des",
    nargs="?",
    type=str,
    default=None,
    dest="destination",
    help="The path where the languages will be saved",
)
optional.add_argument(
    "--multi-thread",
    "-m",
    action=argparse.BooleanOptionalAction,
    default=False,
    dest="multithread",
    help="If you want to use multiple threads simultaneously",
)
optional.add_argument(
    "--threads",
    "-t",
    type=int,
    default=0,
    dest="threadnum",
    help="Number of threads to use",
)
optional.add_argument(
    "-d",
    "--debug",
    help="Print debugging statements",
    action="store_const",
    dest="loglevel",
    const=logging.DEBUG,
    default=logging.WARNING,
)
optional.add_argument(
    "-v",
    "--verbose",
    help="Increase output verbosity",
    action="store_const",
    dest="loglevel",
    const=logging.INFO,
)


# Execute the parse_args() method
args = parser.parse_args()
# print("Args: ", args)

# Set log level (Warning by default)
logging.basicConfig(level=args.loglevel)


def funcWrapper(lang):
    fetch_set(lang, args.destination)


if __name__ == "__main__":
    if not args.multithread:
        for language in args.languages:
            fetch_set(language, args.destination)

    else:
        threads = args.threadnum
        if threads <= 0:
            threads = None

        logging.debug("Starting pooling")
        with multiprocessing.Pool(processes=threads) as pool:
            for result in pool.imap_unordered(funcWrapper, args.languages):
                pass
