from zipfile import ZipFile

from anki.cards import Card
from anki.utils import stripHTML

from .config import DeckConfig, PATH_CHARACTERS
from .util import MaobiException


def _get_character(card: Card, config: DeckConfig) -> str:
    """ Extracts the character to write from `card`.

    Returns:
        character (str): The character contained in field `config.field` of `card`.

    Raises:
        MaobiException:
            - If there is no field called `deck.field` in `card`.
            - If the field called `config.field` is empty.
            - If the field called `config.field` contains more than one character.

    """

    # Check that the character field is really there
    note = card.note()
    note_type = note.model()["name"]
    field_name = config.field

    if field_name not in note:
        raise MaobiException(f"There is no field '{field_name}' in note type {note_type}!")

    # Check that the character is really exactly one character
    character = note[field_name]
    character = stripHTML(character)

    if len(character) == 0:
        raise MaobiException(f"Field '{field_name}' was empty!")

    if len(character) > 1:
        raise MaobiException(f"Expected a single character, but was '{character}'!")

    return character


def _load_character_data(character: str) -> str:
    """ Reads the character data for `character` from `characters.zip`.

    Returns:
        character_data (str): The character data for `character`.

    Raises:
        MaobiException: If data for `character` was not found.

    """

    # Open the zip file and read a single characters' data directly without extracting everything
    with ZipFile(PATH_CHARACTERS, "r") as myzip:
        try:
            with myzip.open(f"data/{character}.json") as f:
                character_data = f.read().decode("utf-8")
                return character_data
        except Exception:
            raise MaobiException(f"Character '{character}' not found!")