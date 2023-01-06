import json
import logging
from os import fspath
from pathlib import Path


def get_wordset_language(setFilePath) -> str:
    """
    Parse the file name and extract the language.
    By default, the language is composed by the first two characters of the language.
    """
    fileName = Path(setFilePath).stem
    language = fileName.rsplit("_", 1)[0]

    logging.debug(f"Getting file language from: {setFilePath}")
    logging.debug(f"Language from set is: {language}")

    return language


def get_wordsets(directory=None, data_file_path=None, store=False):
    wordsets_files: list[dict] = []

    if directory is None:
        directory = (Path() / "sets").resolve()
    else:
        if not Path(directory).is_dir():
            logging.critical("Directory specified is not a folder")
            return

    if data_file_path is None:
        # Set the same directory as the sets
        data_file_path = directory
    else:
        if not Path(data_file_path).is_dir():
            logging.error("Data file path is not a directory. No file will be saved")
            store = False

    # Check if we already have a data file for this directory
    # If is there is already, then we just return the contents
    # TODO: verify that the data file exists and if new files are added
    if not store and data_file_path:
        dataPath = Path(data_file_path / "wordsets.json").resolve()
        if dataPath.exists:
            logging.debug('File "wordsets.json" already exists in the directory')
            with open(dataPath, mode="r", encoding="utf-8") as f:
                logging.debug('Returning "wordsets.json" content...')
                return json.load(f)

    # Get all nouns, in theory all nouns should have their adjectives
    # if not, then we ignore them with a warning.
    # By default, the kds extension is used for file sets
    logging.info(f"Reading wordsets files from {directory}...")
    setFiles = list(directory.glob("*_nouns.kds"))

    if not setFiles:
        logging.error("No wordsets found in the directory")
        return

    # Sort the files alphabetically if they are not
    setFiles = sorted(setFiles)

    # Create a new set to track the already sorted files
    alreadySorted = set()
    for file in setFiles:
        lang = get_wordset_language(file)

        if lang in alreadySorted:
            logging.debug(f'Language "{lang}" already sorted. Ignoring')
            continue

        noun = file
        adj = Path(directory / f"{lang}_adj.kds").resolve()

        if not adj:
            logging.warning(f"No matching adjective file found for {lang} language")
            alreadySorted.add(lang)
            continue

        logging.debug(f"Added to wordsets:\n{lang} - Noun: {noun} - Adj: {adj}")
        wordsets_files.append(
            {
                "lang": lang,
                "noun": fspath(noun),
                "adj": fspath(adj),
            }
        )

    logging.debug("Current wordsets data:")
    logging.debug(wordsets_files)

    if store:
        setData = json.dumps(wordsets_files, indent=2)
        path = Path(data_file_path / "wordsets.json").resolve()

        logging.info(f"Saving wordsets data to {path}")
        with open(path, mode="w+", encoding="utf-8") as f:
            f.write(setData)

    # end return
    return wordsets_files


# If this module is being run directly, just parse the
# data and save the results in the default directory: ./sets
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    get_wordsets(None, None, True)
