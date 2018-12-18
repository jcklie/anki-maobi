# Configuration

Before using *maobi*, it has to be specified for which decks and note types the add-on should be enabled. The field that contains the character to write also has to be specified.

In order to tell *maobi* these values, you need to edit the add-on configuration. For that, go to the Addons-Config via **Tools** → **Add-ons**. Select **maobi** and then click on **Config**.

The configuration itself is written in JSON. The default configuration is

    {
        "decks": [

        ],
        "note_types": [

        ],
        "field_name": "Hanzi"
    }

The following paragraphs explain the values in detail.

#### Decks

This specifies for which decks *maobi* should be enabled. It expects a list of *full* deck name strings. The full name is the name you get when you try to rename a deck. For instance, in order to enable it for the decks `Chinese::Characters` and `Heisig Simplified Hanzi`, the config looks like

    {
        "decks": [
            "Chinese::Characters",
            "Heisig Simplified Hanzi"
        ],
       ...
    }

#### Note types

This specifies for which note types *maobi* should be enabled. It expects a list of note type name strings. For instance, in order to enable it for the note types `Writing` and `Character`, the config looks like

    {
        "note_types": [
            "Writing",
            "Character"
        ],
        ...
    }

#### Field name

The field name tells the add-on which field contains the character that should be quizzed. If for instance, the character is in the `Hanzi` field, then the config looks like

    {
        ...,
        "field_name": "Hanzi"
    }
