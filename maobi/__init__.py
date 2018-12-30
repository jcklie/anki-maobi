from collections import namedtuple
import os 
from string import Template
import sys
from urllib.parse import quote
from zipfile import ZipFile

from anki.hooks import addHook
from anki.cards import Card
from aqt import mw

PATH_MAOBI = os.path.dirname(os.path.realpath(__file__))
PATH_HANZI_WRITER = os.path.join(PATH_MAOBI, "hanzi-writer.min.js")
PATH_CHARACTERS = os.path.join(PATH_MAOBI, "characters.zip")
PATH_RICE_GRID = os.path.join(PATH_MAOBI, "rice.svg")
PATH_FIELD_GRID = os.path.join(PATH_MAOBI, "field.svg")

TARGET_DIV = "character-target-div"

TEMPLATE = Template("""
<style scoped>
#$target_div {
    display: inline-block;

    // We use outline instead of border in order to not cut into the background grid image: it 
    // can be that the border stroke width would be divided between inside and outside the div,
    // therefore overlapping with the background.
    outline-color: rgb(0, 0, 0);
    outline-style: solid;
    outline-width: 1px;
    outline-offset: -1px;
}

$styles
</style>

$html

<script>
$hanzi_writer_script
</script>

<script>
onShownHook.push(function () {
    var writer = HanziWriter.create('$target_div', '$character', {
    width: $size,
    height: $size,
    showCharacter: false,
    showOutline: false,
    showHintAfterMisses: 1,
    highlightOnComplete: true,
    padding: 0,
    charDataLoader: function(char, onComplete) {
    var charData = $character_data;
        onComplete(charData);
    }
    });
    writer.quiz();
});
</script>
""")

DeckConfig = namedtuple("DeckConfig", ["name", "template", "field"])

class MaobiException(Exception):
    pass

class MaobiConfig:

    DEFAULT_SIZE = 200
    DEFAULT_GRID = "rice"

    def __init__(self, config_json: dict):
        self.debug = config_json.get("debug", False)
        self.grid = config_json.get("grid", MaobiConfig.DEFAULT_GRID)
        self.size = config_json.get("size", MaobiConfig.DEFAULT_SIZE)
        self.decks = []

        for deck in config_json.get("decks", []):
            deck_config = DeckConfig(deck["name"], deck["template"], deck["field"])
            self.decks.append(deck_config)


def maobi_hook(html: str, card: Card, context: str) -> str:  
    # Only show the quiz on the front side, else it can lead to rendering issues
    if context not in {"reviewQuestion", "clayoutQuestion", "previewQuestion"}:
        return html

    # This reads from the config.json in the addon folder
    config_json = mw.addonManager.getConfig(__name__)
    config = MaobiConfig(config_json)

    # Search the active deck configuration
    deck = _search_active_deck_config(card, config)

    # Return if we did not find it
    if not deck:
        return html
    
    # Get the character to write and the corresponding character data
    try:
        character = _get_character(card, deck, config)
        character_data = _load_character_data(character)
    except MaobiException as e:
        _error(e.message)
        return html

    # Style the character div depending on the configuration
    styles = []

    # Add the background grid
    hanzi_grid = _build_hanzi_grid_style(config.grid)
    styles.append(hanzi_grid)

    # Load the hanzi writer JavaScript
    with open(PATH_HANZI_WRITER, "r") as f:
        hanzi_writer_script = f.read()

    # Render the template
    data = {
        "html": html,
        "hanzi_writer_script": hanzi_writer_script,
        "target_div": TARGET_DIV,
        "character": character,
        "character_data": character_data,
        "size": config.size,
        "styles": "\n".join(styles)
    }

    result = TEMPLATE.substitute(data)

    return result

def _search_active_deck_config(card: Card, config: MaobiConfig) -> 'Optional[DeckConfig]':
    """ Searches the active deck configuration.
    
    Returns:
        The active deck configuration if maobi is active for this card else `None`.

    """
    deck_name = mw.col.decks.current()["name"]
    template_name = card.template()["name"]

    note = card.note()
    note_type = note.model()["name"]

    # Search for the correct configuration
    for deck in config.decks:
        # Return if we find it
        if deck.name == deck_name and deck.template == template_name:
            return deck
    else:
        if config.debug:
            _error(f"No configuration found for deck: '{deck_name}' and template '{template_name}")

        return None


def _get_character(card: Card, deck: DeckConfig, config: MaobiConfig) -> str:
    """ Extracts the character to write from `card`.

    Returns:
        character (str): The character contained in field `config.field` of `card`.
    
    Raises:
        MaobiException: 
            - If there is no field called `config.field`.
            - If the field called `config.field` is empty.
            - If the field called `config.field` contains more than one character.

    """

    # Check that the character field is really there
    note = card.note()
    note_type = note.model()["name"]
    field_name = deck.field

    if field_name not in note:
        raise MaobiException(f"There is no field '{field_name}' in note type {note_type}!")

    # Check that the character is really exactly one character
    character = note[field_name]

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
        except:
            raise MaobiException(f"Character '{character}' not found!")


def _build_hanzi_grid_style(background_type: str) -> str:
    """ Generate the JavaScript snippet that sets the background specified by `background_type`.

    Right now, legal values for `background_type` are "rice" or "field". The SVG itself is generated 
    with `scripts/generate_hanzi_grids.py`.
    """

    backgrounds = {
        "rice": PATH_RICE_GRID,
        "field": PATH_FIELD_GRID,
    }

    # Do nothing for unknown background type
    if background_type not in backgrounds:
        return ""

    # We use CSS here to set the style, as it seems the easiest. I considered using inline CSS 
    # style directly, but that seemed less maintainable to generate. I also tried 
    # `background-size: covered;` , but that made the image cut off at the right side.
    style = Template("""
#$target_div {
    background: url('data:image/svg+xml;charset=utf8,$svg_data');
    background-size: 100% 100%;
}
""")

    # Load the SVG data
    with open(backgrounds[background_type]) as f:
        svg_data = f.read()

    return style.substitute(target_div=TARGET_DIV, svg_data=quote(svg_data))


def _error(msg: str):
    """ Raises an error with message `msg`. This will cause a popup in Anki. """
    sys.stderr.write(msg)
    sys.stderr.write("\n")


addHook('prepareQA', maobi_hook)