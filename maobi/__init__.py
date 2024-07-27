from anki.buildinfo import version
from anki.hooks import wrap


def hook_quiz():
    from aqt import gui_hooks

    from .quiz import maobi_review_hook

    gui_hooks.card_will_show.append(maobi_review_hook)


def hook_add_config_button():
    from aqt import gui_hooks

    from .config import maobi_add_config_button_hook

    gui_hooks.card_layout_will_show.append(maobi_add_config_button_hook)


version = tuple(int(p) for p in version.split("."))
required_version = (2, 1, 33)

if version < required_version:
    from maobi.util import error

    error(
        "Maobi needs a newer Anki version than installed! Minimum: "
        + str(required_version)
    )
else:
    hook_quiz()
    hook_add_config_button()
