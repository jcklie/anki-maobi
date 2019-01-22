from collections import namedtuple
from enum import Enum

from aqt import mw
from aqt.qt import *

from maobi.util import debug, error

GridType = namedtuple("GridType", ["name", "label"])


class GridTypes(Enum):
    NONE = GridType("none", "None")
    FIELD = GridType("field", "Field 田")
    RICE = GridType("rice", "Rice 米")

    @staticmethod
    def from_name(name: str) -> GridType:
        values = {e.value.name: e.value for e in GridTypes}

        if name not in values:
            error(f"{name} is not a valid grid option!")

        return values.get(name, MaobiConfig.DEFAULT_GRID)


class DeckConfig:
    """ DeckConfig is the Maobi config for a specific deck. """

    def __init__(
        self, deck: str, template: str, field: str, grid: GridType, size: int, enabled: bool
    ):
        self.deck = deck
        self.template = template
        self.field = field
        self.grid = grid
        self.size = size
        self.enabled = enabled

    def __hash__(self):
        # A config is unique per (deck,template,field combination). Other fields are neglected.
        return hash((self.deck, self.template, self.field))

    def __eq__(self, other):
        if isinstance(other, DeckConfig):
            return self.deck == other.deck and self.template == other.template
        return False

    def __str__(self) -> str:
        return f"DeckConfig<Deck: '{self.deck}', Template: '{self.template}', Field: '{self.field}', Grid: '{self.grid.name}', Size: '{self.size}', Enabled: '{self.enabled}'>"


class MaobiConfig:
    """ MaobiConfig is the config as loaded from config.json. """

    DEFAULT_SIZE = 200
    DEFAULT_GRID = GridTypes.RICE.value
    DEFAULT_ENABLED = True

    def __init__(self, config_json: dict):
        self.debug = config_json.get("debug", False)
        self.decks = set()

        for e in config_json.get("decks", []):
            deck_config = DeckConfig(
                e["deck"],
                e["template"],
                e["field"],
                GridTypes.from_name(e.get("grid", MaobiConfig.DEFAULT_GRID.name)),
                e.get("size", MaobiConfig.DEFAULT_SIZE),
                e.get("enabled", MaobiConfig.DEFAULT_ENABLED),
            )
            self.decks.add(deck_config)

    @staticmethod
    def load() -> "MaobiConfig":
        config_json = mw.addonManager.getConfig(__name__)
        config = MaobiConfig(config_json)
        return config

    def search_active_deck_config(
        self, deck_name: str, template_name: str
    ) -> "Optional[DeckConfig]":
        """ Searches the active deck configuration.
        
        Returns:
            The active deck configuration if maobi is active for this card else `None`.

        """
        # Search for the correct configuration
        for e in self.decks:
            # Return if we find it
            if e.deck == deck_name and e.template == template_name:
                return e
        else:
            debug(self, f"No configuration found for: '{deck_name}' and template '{template_name}")
            return None

    def as_object(self) -> dict:
        result = {"decks": []}

        if self.debug:
            result["debug"] = self.debug

        for e in self.decks:
            deck = {
                "deck": e.deck,
                "template": e.template,
                "grid": e.grid.name,
                "size": e.size,
                "field": e.field,
                "enabled": e.enabled,
            }
            result["decks"].append(deck)

        return result

    def __str__(self) -> str:
        return str(self.as_object())


class MaobiConfigDialog(QDialog):
    def __init__(self, parent, card):
        super().__init__(parent)

        self._parent = parent
        self._card = card

        self.setWindowTitle("Maobi Configuration")

        self._enabled = self._build_enabled_checkbox()
        self._field = self._build_field_combo_box()
        self._grid = self._build_grid_combo_box()
        self._size = self._build_size_spin_box()

        formGroupBox = QGroupBox("Edit Maobi configuration")
        layout = QFormLayout()
        layout.addRow(QLabel("Enabled:"), self._enabled)
        layout.addRow(QLabel("Field:"), self._field)
        layout.addRow(QLabel("Grid:"), self._grid)
        layout.addRow(QLabel("Size:"), self._size)
        formGroupBox.setLayout(layout)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self._accept)
        buttonBox.rejected.connect(self._reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(formGroupBox)
        mainLayout.addWidget(buttonBox)

        self._load_config()

        self.setLayout(mainLayout)
        self.adjustSize()
        self.show()

    def _build_enabled_checkbox(self) -> QCheckBox:
        checkBox = QCheckBox(self)
        checkBox.setChecked(MaobiConfig.DEFAULT_ENABLED)
        return checkBox

    def _build_field_combo_box(self) -> QComboBox:
        fields = self._card.note().keys()
        comboBox = QComboBox()
        comboBox.addItems(fields)
        return comboBox

    def _build_grid_combo_box(self) -> QComboBox:
        comboBox = QComboBox()

        for e in GridTypes:
            grid_type = e.value
            comboBox.addItem(grid_type.label, grid_type)

        idx = comboBox.findData(MaobiConfig.DEFAULT_GRID)
        comboBox.setCurrentIndex(idx)
        return comboBox

    def _build_size_spin_box(self) -> QSpinBox:
        spinBox = QSpinBox()
        spinBox.setMinimum(0)
        spinBox.setMaximum(1000)
        spinBox.setValue(MaobiConfig.DEFAULT_SIZE)
        return spinBox

    def _accept(self):
        self._save_config()
        self.close()
        self._parent.redraw()

    def _reject(self):
        self.close()

    def _load_config(self):
        config = MaobiConfig.load()
        deck_config = self._find_config_for_deck()

        # Nothing to load, just return
        if not deck_config:
            # debug(config, "No config found")
            return

        # Find the right field
        idx = self._field.findText(deck_config.field)
        self._field.setCurrentIndex(idx)

        self._enabled.setChecked(deck_config.enabled)

        # Set grid type
        idx = self._grid.findData(deck_config.grid)
        self._grid.setCurrentIndex(idx)

        self._size.setValue(deck_config.size)

    def _save_config(self):
        config = MaobiConfig.load()
        deck_config = self._find_config_for_deck()

        deck_name = self._deck_name()
        template_name = self._template_name()
        field_name = self._field_name()
        enabled = self._is_enabled()
        grid = self._grid_name()
        size = self._size_value()

        new_deck_config = DeckConfig(deck_name, template_name, field_name, grid, size, enabled)

        # Remove the old config if it existed, then add the new one
        config.decks.discard(deck_config)
        config.decks.add(new_deck_config)

        # Write new config to disk
        mw.addonManager.writeConfig(__name__, config.as_object())

    def _find_config_for_deck(self):
        config = MaobiConfig.load()
        deck_name = self._deck_name()
        template_name = self._template_name()
        return config.search_active_deck_config(deck_name, template_name)

    def _deck_name(self) -> str:
        return mw.col.decks.current()["name"]

    def _template_name(self) -> str:
        return self._card.template()["name"]

    def _field_name(self) -> str:
        return self._field.currentText()

    def _is_enabled(self) -> bool:
        return self._enabled.isChecked()

    def _grid_name(self) -> GridType:
        idx = self._grid.currentIndex()
        return self._grid.itemData(idx)

    def _size_value(self) -> int:
        return self._size.value()


def add_maobi_button(self):
    maobi_button = QPushButton("Maobi")
    maobi_button.setAutoDefault(False)
    maobi_button.clicked.connect(lambda: MaobiConfigDialog(self, self.card))

    self.buttons.insertWidget(4, maobi_button)
