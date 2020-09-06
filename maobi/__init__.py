from anki.hooks import wrap


def hook_quiz():
    from .quiz import maobi_review_hook

    try:
        # Anki >= 2.1.20
        from aqt import gui_hooks

        gui_hooks.card_will_show.append(maobi_review_hook)
    except:
        # Use the legacy hook instead
        from anki.hooks import addHook

        addHook("prepareQA", maobi_review_hook)


def hook_add_config_button():
    try:
        from aqt import gui_hooks
        from .config import maobi_add_config_button_hook

        gui_hooks.card_layout_will_show.append(maobi_add_config_button_hook)
    except:
        from aqt.clayout import CardLayout
        from .config import maobi_add_config_button_legacy_patch

        CardLayout.setupButtons = wrap(CardLayout.setupButtons, maobi_add_config_button_legacy_patch)


hook_quiz()
hook_add_config_button()
