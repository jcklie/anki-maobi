from anki.cards import Card

from aqt import mw

from .config import MaobiConfig, PATH_HANZI_WRITER
from .looping_animation import draw_looping_animation
from .quiz import draw_quiz
from .util import debug, _build_error_message


def maobi_hook(html: str, card: Card, context: str) -> str:
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

    # Load the hanzi writer JavaScript
    with open(PATH_HANZI_WRITER, "r") as f:
        hanzi_writer_script = f.read()

    # Make sure to add the script only once here
    html += "\n<script>" + hanzi_writer_script + "</script>"

    # Draw the things
    try:
        # Only show the quiz on the front side, else it can lead to rendering issues
        if context in {"reviewQuestion", "clayoutQuestion", "previewQuestion"}:
            html = draw_quiz(html, card, config)

        html = draw_looping_animation(html, card, config)
    except Exception as e:
        debug(maobi_config, str(e))
        return _build_error_message(html, str(e))

    return html