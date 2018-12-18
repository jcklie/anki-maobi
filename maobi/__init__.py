import os 
from string import Template
import sys
from zipfile import ZipFile

from anki.hooks import addHook

from aqt import mw

PATH_MAOBI = os.path.dirname(os.path.realpath(__file__))
PATH_HANZI_WRITER = os.path.join(PATH_MAOBI, "hanzi-writer.min.js")
PATH_CHARACTERS = os.path.join(PATH_MAOBI, "characters.zip")

TEMPLATE = Template("""
$html

<script>$hanzi_writer_script</script>

<script>
onShownHook.push(function () {
    var writer = HanziWriter.create('character-target-div', '$character', {
    width: 150,
    height: 150,
    showCharacter: false,
    showOutline: false,
    showHintAfterMisses: 1,
    highlightOnComplete: true,
    padding: 5,
    charDataLoader: function(char, onComplete) {
    var charData = $character_data;
        onComplete(charData);
    }
    });
    writer.quiz();
});
</script>
""")

def prepare(html: str, card: str, context: str) -> str:
    # Only show the quiz on the front side, else it can lead to rendering issues
    if context not in {"reviewQuestion", "clayoutQuestion", "previewQuestion"}:
        return html

    # This reads from the config.json in the addon folder
    config = mw.addonManager.getConfig(__name__)

    # Only show quiz when the addon is enabled for this deck
    decks = config["decks"]
    deck_name = mw.col.decks.current()["name"]

    if deck_name not in decks:
        return html

    # Only show quiz when the addon is enabled for this note type
    note_types = config["note_types"]
    note = card.note()
    note_type = note.model()["name"]

    if note_type not in note_types:
        return html
    
    # Get the character that will be quizzed from the note
    field_name = config["field_name"]

    # Check that the field is really there
    if field_name not in note:
        error(f"There is no field '{field_name}' in note type {note_type}!")
        return html

    # Check that the character is really exactly one character
    character = note[field_name]

    if len(character) == 0:
        error(f"Field '{field_name}' was empty!")
        return html

    if len(character) > 1:
        error(f"Expected a single character, but was '{character}'!")
        return html

    with ZipFile(PATH_CHARACTERS, "r") as myzip:
        try:
            with myzip.open(f"data/{character}.json") as f:
                character_data = f.read().decode("utf-8")
        except:
            error(f"Character '{character}' not found!")
            return html

    with open(PATH_HANZI_WRITER, "r") as f:
        hanzi_writer_script = f.read()

    data = {
        "html": html,
        "hanzi_writer_script": hanzi_writer_script,
        "character": character,
        "character_data": character_data,
    }

    result = TEMPLATE.substitute(data)

    return result

def error(msg: str):
    """ Raises an error with message `msg`. This will cause a popup in Anki. """
    sys.stderr.write(msg)
    sys.stderr.write("\n")

addHook('prepareQA', prepare)