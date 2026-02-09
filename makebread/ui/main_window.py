"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget,
    QToolBar, QLineEdit, QPushButton, QLabel,
    QMessageBox, QSplitter, QStatusBar, QMenuBar
)
from PySide6.QtCore import Qt, Slot, QUrl
from PySide6.QtGui import QAction, QIcon, QDesktopServices

from makebread.i18n import _
from makebread.models.recipe import Recipe, RecipeStore
from makebread.ui.recipe_view import RecipeViewWidget
from makebread.ui.recipe_editor import RecipeEditorDialog
from makebread.ui.print_recipe import print_recipe
from makebread.ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, store: RecipeStore):
        super().__init__()
        self.store = store
        self.setWindowTitle(_("makeBread — Bread Machine Recipe Manager"))
        self.setMinimumSize(900, 600)
        self._setup_ui()
        self._setup_menubar()
        self._setup_toolbar()
        self._load_recipes()

    def _setup_ui(self):
        # Main splitter: recipe list | recipe view
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: search + recipe list
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(4, 4, 4, 4)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("Search recipes..."))
        self.search_input.textChanged.connect(self._on_search)
        left_layout.addWidget(self.search_input)

        self.recipe_list = QListWidget()
        self.recipe_list.currentRowChanged.connect(self._on_recipe_selected)
        left_layout.addWidget(self.recipe_list)

        splitter.addWidget(left)

        # Right panel: recipe view
        self.recipe_view = RecipeViewWidget()
        splitter.addWidget(self.recipe_view)

        splitter.setSizes([280, 620])
        self.setCentralWidget(splitter)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _setup_menubar(self):
        menubar = self.menuBar()

        # Edit menu
        edit_menu = menubar.addMenu(_("&Edit"))
        edit_menu.addAction(_("&Settings..."), self._on_settings, "Ctrl+,")

        # Help menu
        help_menu = menubar.addMenu(_("&Help"))
        help_menu.addAction(_("&About makeBread"), self._on_about)
        help_menu.addAction(_("Donate ♥"), self._on_donate)

    def _setup_toolbar(self):
        toolbar = QToolBar(_("Main Toolbar"))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        add_action = QAction(_("&New Recipe"), self)
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self._on_add_recipe)
        toolbar.addAction(add_action)

        edit_action = QAction(_("&Edit"), self)
        edit_action.setShortcut("Ctrl+E")
        edit_action.triggered.connect(self._on_edit_recipe)
        toolbar.addAction(edit_action)

        delete_action = QAction(_("&Delete"), self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self._on_delete_recipe)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        random_action = QAction(_("🎲 &Random"), self)
        random_action.setShortcut("Ctrl+R")
        random_action.triggered.connect(self._on_random)
        toolbar.addAction(random_action)

        print_action = QAction(_("🖨️ &Print"), self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self._on_print)
        toolbar.addAction(print_action)

        toolbar.addSeparator()

        self.fav_action = QAction(_("☆ &Favorite"), self)
        self.fav_action.setShortcut("Ctrl+F")
        self.fav_action.triggered.connect(self._on_toggle_favorite)
        toolbar.addAction(self.fav_action)

        filter_fav_action = QAction(_("♥ Favorites &Only"), self)
        filter_fav_action.setCheckable(True)
        filter_fav_action.triggered.connect(self._on_filter_favorites)
        toolbar.addAction(filter_fav_action)
        self.filter_fav_action = filter_fav_action

    def _load_recipes(self, select_id: int = None):
        """Load all recipes into the list."""
        self.recipes = self.store.get_all()
        self.recipe_list.clear()
        select_row = 0
        for i, r in enumerate(self.recipes):
            label = f"★ {r.name}" if r.favorite else r.name
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, r.id)
            self.recipe_list.addItem(item)
            if select_id and r.id == select_id:
                select_row = i
        self.status.showMessage(_("{count} recipes").format(count=len(self.recipes)))
        if self.recipes:
            self.recipe_list.setCurrentRow(select_row)

    @Slot(int)
    def _on_recipe_selected(self, row: int):
        if 0 <= row < len(self.recipes):
            recipe = self.store.get(self.recipes[row].id)
            if recipe:
                self.recipe_view.show_recipe(recipe)
                self.fav_action.setText(
                    _("★ Un&favorite") if recipe.favorite else _("☆ &Favorite")
                )

    @Slot(str)
    def _on_search(self, text: str):
        if not text.strip():
            self._load_recipes()
            return
        try:
            self.recipes = self.store.search(text)
        except Exception:
            self.recipes = []
        self.recipe_list.clear()
        for r in self.recipes:
            item = QListWidgetItem(r.name)
            item.setData(Qt.ItemDataRole.UserRole, r.id)
            self.recipe_list.addItem(item)
        self.status.showMessage(
            _("{count} results for '{query}'").format(count=len(self.recipes), query=text)
        )

    @Slot()
    def _on_add_recipe(self):
        dialog = RecipeEditorDialog(self)
        if dialog.exec():
            recipe = dialog.get_recipe()
            rid = self.store.save(recipe)
            self._load_recipes(select_id=rid)

    @Slot()
    def _on_edit_recipe(self):
        row = self.recipe_list.currentRow()
        if row < 0:
            return
        recipe = self.store.get(self.recipes[row].id)
        if not recipe:
            return
        dialog = RecipeEditorDialog(self, recipe=recipe)
        if dialog.exec():
            updated = dialog.get_recipe()
            self.store.save(updated)
            self._load_recipes(select_id=updated.id)

    @Slot()
    def _on_delete_recipe(self):
        row = self.recipe_list.currentRow()
        if row < 0:
            return
        recipe = self.recipes[row]
        reply = QMessageBox.question(
            self, _("Delete Recipe"),
            _("Delete '{name}'?").format(name=recipe.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.store.delete(recipe.id)
            self._load_recipes()

    @Slot()
    def _on_random(self):
        recipe = self.store.random()
        if recipe:
            self.recipe_view.show_recipe(recipe)
            # Select in list
            for i in range(self.recipe_list.count()):
                if self.recipe_list.item(i).data(Qt.ItemDataRole.UserRole) == recipe.id:
                    self.recipe_list.setCurrentRow(i)
                    break
            self.status.showMessage(_("Random pick: {name}").format(name=recipe.name))

    @Slot()
    def _on_print(self):
        row = self.recipe_list.currentRow()
        if row < 0:
            return
        recipe = self.store.get(self.recipes[row].id)
        if recipe:
            print_recipe(recipe, self)

    @Slot()
    def _on_toggle_favorite(self):
        row = self.recipe_list.currentRow()
        if row < 0:
            return
        recipe = self.store.get(self.recipes[row].id)
        if not recipe:
            return
        recipe.favorite = not recipe.favorite
        self.store.save(recipe)
        self._load_recipes(select_id=recipe.id)
        self.status.showMessage(
            _("Added to favorites: {name}").format(name=recipe.name) if recipe.favorite
            else _("Removed from favorites: {name}").format(name=recipe.name)
        )

    @Slot(bool)
    def _on_filter_favorites(self, checked: bool):
        if checked:
            self.recipes = [r for r in self.store.get_all() if r.favorite]
            self.recipe_list.clear()
            for r in self.recipes:
                item = QListWidgetItem(f"★ {r.name}")
                item.setData(Qt.ItemDataRole.UserRole, r.id)
                self.recipe_list.addItem(item)
            self.status.showMessage(
                _("{count} favorites").format(count=len(self.recipes))
            )
            if self.recipes:
                self.recipe_list.setCurrentRow(0)
        else:
            self._load_recipes()

    @Slot()
    def _on_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Refresh current recipe view with new settings
            row = self.recipe_list.currentRow()
            if 0 <= row < len(self.recipes):
                recipe = self.store.get(self.recipes[row].id)
                if recipe:
                    self.recipe_view.show_recipe(recipe)

    @Slot()
    def _on_donate(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(_("Donate ♥"))
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(_(
            "<p>makeBread is free software.</p>"
            "<p>If you find it useful, consider supporting development:</p>"
            "<p>❤️ <b>GitHub Sponsors:</b> <a href='https://github.com/sponsors/yeager'>"
            "github.com/sponsors/yeager</a></p>"
            "<p>🇸🇪 <b>Swish:</b> +46702526206 — "
            "<a href='swish://payment?payee=0702526206&message=makeBread'>"
            "Open Swish</a></p>"
        ))
        msg.exec()

    @Slot()
    def _on_about(self):
        QMessageBox.about(
            self,
            _("About makeBread"),
            _(
                "<h3>makeBread</h3>"
                "<p>Bread Machine Recipe Manager</p>"
                "<p>© 2026 Daniel Nylander</p>"
                "<p>License: GPL-3.0-or-later</p>"
                "<p><a href='https://github.com/yeager/makebread'>"
                "github.com/yeager/makebread</a></p>"
            ),
        )
