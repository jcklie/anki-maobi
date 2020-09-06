from collections import namedtuple
from enum import Enum

from aqt import mw
from aqt.clayout import CardLayout
from aqt.qt import *

from .util import debug, error

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
        self,
        deck: str,
        template: str,
        field: str,
        grid: GridType,
        size: int,
        leniency: int,
        enabled: bool,
        show_hint_after_misses: int,
    ):
        self.deck = deck
        self.template = template
        self.field = field
        self.grid = grid
        self.size = size
        self.leniency = leniency
        self.enabled = enabled
        self.show_hint_after_misses = show_hint_after_misses

    def __hash__(self):
        # A config is unique per (deck,template,field combination). Other fields are neglected.
        return hash((self.deck, self.template, self.field))

    def __eq__(self, other):
        if isinstance(other, DeckConfig):
            return self.deck == other.deck and self.template == other.template
        return False


class MaobiConfig:
    """ MaobiConfig is the config as loaded from config.json. """

    DEFAULT_SIZE = 200
    DEFAULT_GRID = GridTypes.RICE.value
    DEFAULT_ENABLED = True
    DEFAULT_LENIENCY = 100
    DEFAULT_SHOW_HINT_AFTER_MISSES = 3

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
                e.get("leniency", MaobiConfig.DEFAULT_LENIENCY),
                e.get("enabled", MaobiConfig.DEFAULT_ENABLED),
                e.get("show_hint_after_misses", MaobiConfig.DEFAULT_SHOW_HINT_AFTER_MISSES),
            )
            self.decks.add(deck_config)

    @staticmethod
    def load() -> "MaobiConfig":
        config_json = mw.addonManager.getConfig(__name__)
        config = MaobiConfig(config_json)
        return config

    def search_active_deck_config(self, deck_name: str, template_name: str) -> "Optional[DeckConfig]":
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
            debug(
                self, f"No configuration found for: '{deck_name}' and template '{template_name}",
            )
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
                "leniency": e.leniency,
                "enabled": e.enabled,
                "show_hint_after_misses": e.show_hint_after_misses,
            }
            result["decks"].append(deck)

        return result

    def __str__(self) -> str:
        return str(self.as_object())


class MaobiConfigDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self._parent = parent
        self._card_layout = parent

        self.setWindowTitle("Maobi Configuration")

        self._enabled = self._build_enabled_checkbox()
        self._field = self._build_field_combo_box()
        self._grid = self._build_grid_combo_box()
        self._size = self._build_size_spin_box()
        self._leniency = self._build_leniency_slider()
        self._show_hint_after_misses = self._build_show_hint_after_misses_spin_box()

        formGroupBox = QGroupBox("Edit Maobi configuration")
        layout = QFormLayout()
        layout.addRow(QLabel("Enabled:"), self._enabled)
        layout.addRow(QLabel("Field:"), self._field)
        layout.addRow(QLabel("Grid:"), self._grid)
        layout.addRow(QLabel("Size:"), self._size)
        layout.addRow(QLabel("Leniency:"), self._leniency)
        layout.addRow(QLabel("Show hint after misses:"), self._show_hint_after_misses)
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
        fields = self._card_layout.note.keys()
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

    def _build_leniency_slider(self) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(2 * MaobiConfig.DEFAULT_LENIENCY)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(MaobiConfig.DEFAULT_LENIENCY)
        slider.setValue(MaobiConfig.DEFAULT_LENIENCY)
        return slider

    def _build_show_hint_after_misses_spin_box(self) -> QSpinBox:
        spinBox = QSpinBox()
        spinBox.setMinimum(0)
        spinBox.setMaximum(10)
        spinBox.setValue(MaobiConfig.DEFAULT_SHOW_HINT_AFTER_MISSES)
        return spinBox

    def _accept(self):
        self._save_config()
        self.close()
        self._parent.redraw_everything()

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
        self._leniency.setValue(deck_config.leniency)
        self._show_hint_after_misses.setValue(deck_config.show_hint_after_misses)

    def _save_config(self):
        config = MaobiConfig.load()
        deck_config = self._find_config_for_deck()

        deck_name = self._deck_name()
        template_name = self._template_name()
        field_name = self._field_name()
        enabled = self._is_enabled()
        grid = self._grid_name()
        size = self._size_value()
        leniency = self._leniency_value()
        show_hint_after_misses = self._show_hint_after_misses_value()

        new_deck_config = DeckConfig(
            deck_name, template_name, field_name, grid, size, leniency, enabled, show_hint_after_misses,
        )

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
        return self._card_layout.current_template()["name"]

    def _field_name(self) -> str:
        return self._field.currentText()

    def _is_enabled(self) -> bool:
        return self._enabled.isChecked()

    def _grid_name(self) -> GridType:
        idx = self._grid.currentIndex()
        return self._grid.itemData(idx)

    def _size_value(self) -> int:
        return self._size.value()

    def _leniency_value(self) -> int:
        return self._leniency.value()

    def _show_hint_after_misses_value(self) -> int:
        return self._show_hint_after_misses.value()


def maobi_add_config_button_legacy_patch(self):
    maobi_button = QPushButton("Maobi")
    maobi_button.setAutoDefault(False)
    maobi_button.clicked.connect(lambda: MaobiConfigDialog(self))

    self.buttons.insertWidget(4, maobi_button)


def maobi_add_config_button_hook(cardlayout: CardLayout):
    maobi_button = QPushButton("Maobi")
    maobi_button.setAutoDefault(False)
    maobi_button.clicked.connect(lambda: MaobiConfigDialog(cardlayout))

    cardlayout.buttons.insertWidget(4, maobi_button)
