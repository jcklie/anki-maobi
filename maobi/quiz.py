import json
import os
from string import Template
from urllib.parse import quote
from zipfile import ZipFile

from anki.cards import Card
from anki.utils import stripHTML
from aqt import mw
import re

from .config import GridType, DeckConfig, MaobiConfig
from .util import debug, error

PATH_MAOBI = os.path.dirname(os.path.realpath(__file__))
PATH_HANZI_WRITER = os.path.join(PATH_MAOBI, "hanzi-writer.min.js")
PATH_QUIZ_JS = os.path.join(PATH_MAOBI, "quiz.js")
PATH_CHARACTERS = os.path.join(PATH_MAOBI, "characters.zip")
PATH_RICE_GRID = os.path.join(PATH_MAOBI, "rice.svg")
PATH_FIELD_GRID = os.path.join(PATH_MAOBI, "field.svg")

TARGET_DIV = "character-target-div"
REVEAL_BUTTON = "reveal-character-btn"
RESTART_BUTTON = "restart-quiz-btn"

TEMPLATE = Template(
    """
<style scoped>
#$target_div {
    height: ${size}px;
}

#$target_div > div {
    position: absolute;
    left: 50%;
    display: inline-block;

    transition: all 300ms ease-in-out;

    // We use outline instead of border in order to not cut into the background grid image: it 
    // can be that the border stroke width would be divided between inside and outside the div,
    // therefore overlapping with the background.
    outline-color: rgb(0, 0, 0);
    outline-style: solid;
    outline-width: 1px;
    outline-offset: -1px;
}

#$reveal_button, #$restart_button {
    margin: 20px 0;
}

$styles
</style>

$html

<script>
$hanzi_writer_script
</script>

<script>
onShownHook.push(function () {
    var config = {
        size: $size,
        leniency: $leniency,
        targetDiv: '$target_div',
        revealButton: '$reveal_button',
        restartButton: '$restart_button',
        showHintAfterMisses: $show_hint_after_misses,
    };
    
    var data = {
        characters: $characters,
        tones: $tones,
        charactersData: ($characters_data).map(JSON.parse),
    };

    $maobi_quiz_script
});
</script>
"""
)


class MaobiException(Exception):
    def __init__(self, message):
        super(MaobiException, self).__init__(message)


def maobi_review_hook(html: str, card: Card, context: str) -> str:
    # Only show the quiz on the front side, else it can lead to rendering issues
    if context not in {"reviewQuestion", "clayoutQuestion", "previewQuestion"}:
        return html

    # This reads from the config.json in the addon folder
    maobi_config = MaobiConfig.load()

    # Search the active deck configuration
    deck_name = mw.col.decks.current()["name"]
    template_name = card.template()["name"]
    config = maobi_config.search_active_deck_config(deck_name, template_name)

    # Return if we did not find it
    if not config:
        debug(maobi_config, f"Config not found")
        return html

    if not config.enabled:
        debug(maobi_config, f"Config disabled")
        return html

    # Get the character to write and the corresponding character data
    try:
        characters, tones = _get_characters(card, config)
        characters_data = [_load_character_data(c) for c in characters]
    except MaobiException as e:
        debug(maobi_config, str(e))
        return _build_error_message(html, str(e))

    # Style the character div depending on the configuration
    styles = []

    # Add the background grid
    hanzi_grid = _build_hanzi_grid_style(config.grid)
    styles.append(hanzi_grid)

    # Load the hanzi writer JavaScript
    with open(PATH_HANZI_WRITER, "r") as f:
        hanzi_writer_script = f.read()

    # Load the maobi quiz JavaScript
    with open(PATH_QUIZ_JS, "r") as f:
        maobi_quiz_script = f.read()

    # Render the template
    data = {
        "html": html,
        "hanzi_writer_script": hanzi_writer_script,
        "maobi_quiz_script": maobi_quiz_script,
        "target_div": TARGET_DIV,
        "reveal_button": REVEAL_BUTTON,
        "restart_button": RESTART_BUTTON,
        "characters": characters,
        "tones": tones,
        "characters_data": characters_data,
        "size": config.size,
        "leniency": config.leniency / 100.0,
        "show_hint_after_misses": config.show_hint_after_misses,
        "styles": "\n".join(styles),
    }

    result = TEMPLATE.substitute(data)

    return result


def _get_characters(card: Card, config: DeckConfig) -> tuple:
    """ Extracts the characters to write from `card`.

    Returns:
        characters (tuple[list[str], list[str])): The characters contained in field `config.field` of `card`, and
        possibly the tones (extracted from css classes)

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

    characters_html = note[field_name]
    characters = stripHTML(characters_html)

    # extract tones, if possible
    tones = []
    if "span" in characters_html:
        # this is the 'colors' field which has tone information as tone1...4 css classes
        tones = list(re.findall("tone[12345]", characters_html))

    if len(tones) != len(characters):
        tones = []

    # Check that the character is one or more characters
    if len(characters) == 0:
        raise MaobiException(f"Field '{field_name}' was empty!")

    return [c for c in characters], tones


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


def _build_hanzi_grid_style(grid_type: GridType) -> str:
    """ Generate the JavaScript snippet that sets the background specified by `background_type`.

    Right now, legal values for `background_type` are "rice" or "field". The SVG itself is generated 
    with `scripts/generate_hanzi_grids.py`.
    """

    backgrounds = {"rice": PATH_RICE_GRID, "field": PATH_FIELD_GRID}

    # Do nothing for unknown background type
    if grid_type.name not in backgrounds:
        return ""

    # We use CSS here to set the style, as it seems the easiest. I considered using inline CSS
    # style directly, but that seemed less maintainable to generate. I also tried
    # `background-size: covered;` , but that made the image cut off at the right side.
    style = Template(
        """
#$target_div > div {
    background: url('data:image/svg+xml;charset=utf8,$svg_data');
    background-size: 100% 100%;
}
"""
    )

    # Load the SVG data
    with open(backgrounds[grid_type.name]) as f:
        svg_data = f.read()

    return style.substitute(target_div=TARGET_DIV, svg_data=quote(svg_data))


def _build_error_message(html: str, message: str) -> str:
    """ Constructs the HTML for an error text with message `message` over the original html. """
    return f"""<p style="text-align: center; color: red; font-size: large;">
Maobi encountered an error: <br />
{message}
</p>
{html}
"""
