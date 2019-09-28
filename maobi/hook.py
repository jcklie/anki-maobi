from anki.cards import Card

from aqt import mw

from .config import MaobiConfig
from .quiz import draw_quiz
from .util import debug, _build_error_message


def maobi_hook(html: str, card: Card, context: str) -> str:
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
        html = draw_quiz(html, card, config)
    except Exception as e:
        debug(maobi_config, str(e))
        return _build_error_message(html, str(e))

    return html