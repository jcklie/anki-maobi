from anki.hooks import addHook, wrap


def patch_quiz():
    from .quiz import maobi_hook

    addHook("prepareQA", maobi_hook)


def patch_config():
    from aqt.clayout import CardLayout

    from .config import add_maobi_button

    CardLayout.setupButtons = wrap(CardLayout.setupButtons, add_maobi_button)


patch_quiz()
patch_config()
