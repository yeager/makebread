"""Settings dialog for makeBread."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDialogButtonBox, QGroupBox, QCheckBox, QLabel
)
from PySide6.QtCore import QSettings

from makebread.i18n import _
from makebread.utils.units import SYSTEM_US, SYSTEM_METRIC, SYSTEM_IMPERIAL


def get_settings() -> QSettings:
    return QSettings("makeBread", "makeBread")


def get_unit_system() -> str:
    return get_settings().value("unit_system", SYSTEM_US)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Settings"))
        self.setMinimumWidth(400)
        self.settings = get_settings()
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Units group
        units_group = QGroupBox(_("Measurement Units"))
        units_layout = QFormLayout(units_group)

        self.unit_combo = QComboBox()
        self.unit_combo.addItem(_("US (cups, oz, °F)"), SYSTEM_US)
        self.unit_combo.addItem(_("Metric (dl, g, °C)"), SYSTEM_METRIC)
        self.unit_combo.addItem(_("Imperial (fl oz, oz, °C)"), SYSTEM_IMPERIAL)
        units_layout.addRow(_("Unit system:"), self.unit_combo)

        self.auto_convert = QCheckBox(_("Automatically convert units when displaying recipes"))
        units_layout.addRow(self.auto_convert)

        info = QLabel(_("Original values are preserved in the database.\n"
                        "Conversion only affects how recipes are displayed and printed."))
        info.setStyleSheet("color: #888; font-size: 11px;")
        info.setWordWrap(True)
        units_layout.addRow(info)

        layout.addWidget(units_group)

        # Display group
        display_group = QGroupBox(_("Display"))
        display_layout = QFormLayout(display_group)

        self.show_machine = QCheckBox(_("Show machine info in recipe list"))
        display_layout.addRow(self.show_machine)

        self.show_category = QCheckBox(_("Show category badges"))
        display_layout.addRow(self.show_category)

        layout.addWidget(display_group)

        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load(self):
        system = self.settings.value("unit_system", SYSTEM_US)
        idx = self.unit_combo.findData(system)
        if idx >= 0:
            self.unit_combo.setCurrentIndex(idx)
        self.auto_convert.setChecked(
            self.settings.value("auto_convert_units", True, type=bool)
        )
        self.show_machine.setChecked(
            self.settings.value("show_machine_info", True, type=bool)
        )
        self.show_category.setChecked(
            self.settings.value("show_category_badges", True, type=bool)
        )

    def _save_and_accept(self):
        self.settings.setValue("unit_system", self.unit_combo.currentData())
        self.settings.setValue("auto_convert_units", self.auto_convert.isChecked())
        self.settings.setValue("show_machine_info", self.show_machine.isChecked())
        self.settings.setValue("show_category_badges", self.show_category.isChecked())
        self.accept()
