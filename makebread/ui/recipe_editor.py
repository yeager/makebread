"""Recipe editor dialog."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QWidget, QDialogButtonBox, QHeaderView,
    QLabel, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from makebread.i18n import _
from makebread.models.recipe import Recipe, Ingredient, Instruction


CATEGORIES = [
    "white", "wheat", "whole grain", "rye", "sourdough",
    "sweet", "gluten-free", "fruit", "cheese", "herb",
    "dough only", "other"
]

LOAF_SIZES = ["1lb", "1.5lb", "2lb", "2.5lb", "3lb"]

PROGRAMS = [
    "Basic/White", "Whole Wheat", "French", "Sweet",
    "Quick/Rapid", "Dough", "Jam", "Cake",
    "Gluten-Free", "Homemade/Programmable", "Other"
]

CRUST_SETTINGS = ["light", "medium", "dark"]


class RecipeEditorDialog(QDialog):
    def __init__(self, parent=None, recipe: Recipe = None):
        super().__init__(parent)
        self.recipe = recipe
        self.setWindowTitle(_("Edit Recipe") if recipe else _("New Recipe"))
        self.setMinimumSize(650, 550)
        self._setup_ui()
        if recipe:
            self._populate(recipe)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # Tab 1: Basic info
        basic = QWidget()
        form = QFormLayout(basic)

        self.name_edit = QLineEdit()
        form.addRow(_("Name:"), self.name_edit)

        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(60)
        form.addRow(_("Description:"), self.desc_edit)

        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES)
        self.category_combo.setEditable(True)
        form.addRow(_("Category:"), self.category_combo)

        self.loaf_combo = QComboBox()
        self.loaf_combo.addItems(LOAF_SIZES)
        form.addRow(_("Loaf Size:"), self.loaf_combo)

        self.program_combo = QComboBox()
        self.program_combo.addItems(PROGRAMS)
        self.program_combo.setEditable(True)
        form.addRow(_("Program:"), self.program_combo)

        self.crust_combo = QComboBox()
        self.crust_combo.addItems(CRUST_SETTINGS)
        form.addRow(_("Crust:"), self.crust_combo)

        row_h = QHBoxLayout()
        self.brand_edit = QLineEdit()
        self.brand_edit.setPlaceholderText(_("Brand"))
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText(_("Model"))
        row_h.addWidget(self.brand_edit)
        row_h.addWidget(self.model_edit)
        form.addRow(_("Machine:"), row_h)

        self.author_edit = QLineEdit()
        form.addRow(_("Author:"), self.author_edit)

        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("https://...")
        form.addRow(_("Source URL:"), self.source_edit)

        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText(_("comma separated"))
        form.addRow(_("Tags:"), self.tags_edit)

        # Image
        img_row = QHBoxLayout()
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText(_("Path to bread photo (optional)"))
        self.image_path_edit.setReadOnly(True)
        browse_img_btn = QPushButton(_("Browse..."))
        browse_img_btn.clicked.connect(self._browse_image)
        clear_img_btn = QPushButton(_("Clear"))
        clear_img_btn.clicked.connect(lambda: self.image_path_edit.clear())
        img_row.addWidget(self.image_path_edit)
        img_row.addWidget(browse_img_btn)
        img_row.addWidget(clear_img_btn)
        form.addRow(_("Photo:"), img_row)

        tabs.addTab(basic, _("Basic Info"))

        # Tab 2: Ingredients
        ing_tab = QWidget()
        ing_layout = QVBoxLayout(ing_tab)

        self.ing_table = QTableWidget(0, 4)
        self.ing_table.setHorizontalHeaderLabels(
            [_("Amount"), _("Unit"), _("Ingredient"), _("Group")]
        )
        self.ing_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        ing_layout.addWidget(self.ing_table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(_("+ Add Ingredient"))
        add_btn.clicked.connect(self._add_ingredient_row)
        remove_btn = QPushButton(_("- Remove Selected"))
        remove_btn.clicked.connect(self._remove_ingredient_row)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(remove_btn)
        btn_row.addStretch()
        ing_layout.addLayout(btn_row)

        tabs.addTab(ing_tab, _("Ingredients"))

        # Tab 3: Instructions
        inst_tab = QWidget()
        inst_layout = QVBoxLayout(inst_tab)

        self.inst_table = QTableWidget(0, 2)
        self.inst_table.setHorizontalHeaderLabels([_("Step"), _("Instruction")])
        self.inst_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.inst_table.setColumnWidth(0, 50)
        inst_layout.addWidget(self.inst_table)

        btn_row2 = QHBoxLayout()
        add_inst_btn = QPushButton(_("+ Add Step"))
        add_inst_btn.clicked.connect(self._add_instruction_row)
        remove_inst_btn = QPushButton(_("- Remove Selected"))
        remove_inst_btn.clicked.connect(self._remove_instruction_row)
        btn_row2.addWidget(add_inst_btn)
        btn_row2.addWidget(remove_inst_btn)
        btn_row2.addStretch()
        inst_layout.addLayout(btn_row2)

        tabs.addTab(inst_tab, _("Instructions"))

        # Tab 4: Notes
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        self.notes_edit = QTextEdit()
        notes_layout.addWidget(self.notes_edit)
        tabs.addTab(notes_tab, _("Notes"))

        layout.addWidget(tabs)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _add_ingredient_row(self):
        row = self.ing_table.rowCount()
        self.ing_table.insertRow(row)
        for col in range(4):
            self.ing_table.setItem(row, col, QTableWidgetItem(""))

    def _remove_ingredient_row(self):
        row = self.ing_table.currentRow()
        if row >= 0:
            self.ing_table.removeRow(row)

    def _add_instruction_row(self):
        row = self.inst_table.rowCount()
        self.inst_table.insertRow(row)
        self.inst_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.inst_table.setItem(row, 1, QTableWidgetItem(""))

    def _remove_instruction_row(self):
        row = self.inst_table.currentRow()
        if row >= 0:
            self.inst_table.removeRow(row)

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, _("Select bread photo"),
            "", _("Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        )
        if path:
            self.image_path_edit.setText(path)

    def _populate(self, r: Recipe):
        self.name_edit.setText(r.name)
        self.desc_edit.setPlainText(r.description)
        idx = self.category_combo.findText(r.category)
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        else:
            self.category_combo.setCurrentText(r.category)
        idx = self.loaf_combo.findText(r.loaf_size)
        if idx >= 0:
            self.loaf_combo.setCurrentIndex(idx)
        idx = self.program_combo.findText(r.machine_program)
        if idx >= 0:
            self.program_combo.setCurrentIndex(idx)
        else:
            self.program_combo.setCurrentText(r.machine_program)
        idx = self.crust_combo.findText(r.crust_setting)
        if idx >= 0:
            self.crust_combo.setCurrentIndex(idx)
        self.brand_edit.setText(r.machine_brand)
        self.model_edit.setText(r.machine_model)
        self.author_edit.setText(r.author)
        self.source_edit.setText(r.source_url)
        self.tags_edit.setText(", ".join(r.tags))
        self.notes_edit.setPlainText(r.notes)
        if r.image_path:
            self.image_path_edit.setText(r.image_path)

        for ing in r.ingredients:
            row = self.ing_table.rowCount()
            self.ing_table.insertRow(row)
            self.ing_table.setItem(row, 0, QTableWidgetItem(ing.amount))
            self.ing_table.setItem(row, 1, QTableWidgetItem(ing.unit))
            self.ing_table.setItem(row, 2, QTableWidgetItem(ing.name))
            self.ing_table.setItem(row, 3, QTableWidgetItem(ing.group_name))

        for inst in r.instructions:
            row = self.inst_table.rowCount()
            self.inst_table.insertRow(row)
            self.inst_table.setItem(row, 0, QTableWidgetItem(str(inst.step_number)))
            self.inst_table.setItem(row, 1, QTableWidgetItem(inst.text))

    def get_recipe(self) -> Recipe:
        """Build a Recipe from the editor fields."""
        tags_text = self.tags_edit.text().strip()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()] if tags_text else []

        recipe = Recipe(
            name=self.name_edit.text().strip(),
            description=self.desc_edit.toPlainText().strip(),
            category=self.category_combo.currentText(),
            loaf_size=self.loaf_combo.currentText(),
            machine_program=self.program_combo.currentText(),
            crust_setting=self.crust_combo.currentText(),
            machine_brand=self.brand_edit.text().strip(),
            machine_model=self.model_edit.text().strip(),
            author=self.author_edit.text().strip(),
            source_url=self.source_edit.text().strip(),
            notes=self.notes_edit.toPlainText().strip(),
            tags=tags,
            image_path=self.image_path_edit.text().strip(),
        )
        if self.recipe:
            recipe.id = self.recipe.id

        # Ingredients
        for row in range(self.ing_table.rowCount()):
            name = (self.ing_table.item(row, 2) or QTableWidgetItem("")).text().strip()
            if not name:
                continue
            recipe.ingredients.append(Ingredient(
                amount=(self.ing_table.item(row, 0) or QTableWidgetItem("")).text().strip(),
                unit=(self.ing_table.item(row, 1) or QTableWidgetItem("")).text().strip(),
                name=name,
                group_name=(self.ing_table.item(row, 3) or QTableWidgetItem("")).text().strip(),
                sort_order=row,
            ))

        # Instructions
        for row in range(self.inst_table.rowCount()):
            text = (self.inst_table.item(row, 1) or QTableWidgetItem("")).text().strip()
            if not text:
                continue
            recipe.instructions.append(Instruction(
                step_number=row + 1,
                text=text,
            ))

        return recipe
