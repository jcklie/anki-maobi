from anki.hooks import wrap


def patch_quiz():
    from .quiz import maobi_hook

    try:
        # Anki >= 2.1.20
        from aqt import gui_hooks
        gui_hooks.card_will_show.append(maobi_hook)
    except:
        # Use the legacy hook instead
        from anki.hooks import addHook
        addHook("prepareQA", maobi_hook)


def patch_config():
    from aqt.clayout import CardLayout

    from .config import add_maobi_button

    CardLayout.setupButtons = wrap(CardLayout.setupButtons, add_maobi_button)


patch_quiz()
patch_config()
