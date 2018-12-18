import os 
from string import Template
import sys
from zipfile import ZipFile

from anki.hooks import addHook
from anki.cards import Card
from aqt import mw

PATH_MAOBI = os.path.dirname(os.path.realpath(__file__))
PATH_HANZI_WRITER = os.path.join(PATH_MAOBI, "hanzi-writer.min.js")
PATH_CHARACTERS = os.path.join(PATH_MAOBI, "characters.zip")

DEFAULT_SIZE = 200

TEMPLATE = Template("""
$html

<script>$hanzi_writer_script</script>

<script>
onShownHook.push(function () {
    var writer = HanziWriter.create('character-target-div', '$character', {
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

def prepare(html: str, card: Card, context: str) -> str:  
    # Only show the quiz on the front side, else it can lead to rendering issues
    if context not in {"reviewQuestion", "clayoutQuestion", "previewQuestion"}:
        return html

    # This reads from the config.json in the addon folder
    config = mw.addonManager.getConfig(__name__)
    debug = config.get("debug", False)
    decks = config["decks"]

    size = config.get("size", DEFAULT_SIZE)

    # Only show quiz when the addon is enabled for this deck
    deck_name = mw.col.decks.current()["name"]
    template_name = card.template()["name"]

    note = card.note()
    note_type = note.model()["name"]

    # Search for the correct configuration
    for deck in decks:
        # Break if we find it
        if deck["name"] == deck_name and deck["template"] == template_name:
            break
    else:
        # Return if we did not find it
        if debug:
            error(f"No configuration found for deck: '{deck_name}' and template '{template_name}")
        return html
    
    # Get the character that will be quizzed from the note
    field_name = deck["field"]

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
        "size": size,
    }

    result = TEMPLATE.substitute(data)

    return result

def error(msg: str):
    """ Raises an error with message `msg`. This will cause a popup in Anki. """
    sys.stderr.write(msg)
    sys.stderr.write("\n")

addHook('prepareQA', prepare)