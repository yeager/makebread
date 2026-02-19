"""Main application window — GTK4/Adwaita."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, GLib, Pango

from makebread.i18n import _
from makebread.models.recipe import Recipe, RecipeStore
from makebread.ui.recipe_view import RecipeViewWidget
from makebread.ui.recipe_editor import RecipeEditorDialog


class RecipeRow(Gtk.Box):
    """A row in the recipe list."""
    def __init__(self, recipe: Recipe):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.recipe_id = recipe.id
        prefix = "★ " if recipe.favorite else ""
        label = Gtk.Label(label=f"{prefix}{recipe.name}", xalign=0, hexpand=True)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        self.append(label)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_start(8)
        self.set_margin_end(8)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, application, store: RecipeStore):
        super().__init__(application=application)
        self.store = store
        self.recipes = []
        self._filter_favorites = False
        self.set_title(_("makeBread"))
        self.set_default_size(1000, 650)
        self._setup_ui()
        self._setup_actions()
        self._load_recipes()

    def _setup_ui(self):
        # Main layout
        self.split_view = Adw.NavigationSplitView()

        # --- Sidebar ---
        sidebar_page = Adw.NavigationPage(title=_("Recipes"))
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Sidebar header
        sidebar_header = Adw.HeaderBar()
        sidebar_header.set_show_title(True)

        # Menu button
        menu_model = Gio.Menu()
        menu_model.append(_("About makeBread"), "app.about")
        menu_btn = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu_model)
        sidebar_header.pack_end(menu_btn)

        # Add recipe button
        add_btn = Gtk.Button(icon_name="list-add-symbolic", tooltip_text=_("New Recipe"))
        add_btn.connect("clicked", self._on_add_recipe)
        sidebar_header.pack_start(add_btn)

        sidebar_box.append(sidebar_header)

        # Search
        self.search_entry = Gtk.SearchEntry(placeholder_text=_("Search recipes…"))
        self.search_entry.set_margin_start(8)
        self.search_entry.set_margin_end(8)
        self.search_entry.set_margin_top(4)
        self.search_entry.set_margin_bottom(4)
        self.search_entry.connect("search-changed", self._on_search)
        sidebar_box.append(self.search_entry)

        # Toolbar for filter buttons
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        filter_box.set_margin_start(8)
        filter_box.set_margin_end(8)
        filter_box.set_margin_bottom(4)

        self.fav_filter_btn = Gtk.ToggleButton(label=_("♥ Favorites"))
        self.fav_filter_btn.connect("toggled", self._on_filter_favorites)
        filter_box.append(self.fav_filter_btn)

        random_btn = Gtk.Button(label=_("🎲 Random"))
        random_btn.connect("clicked", self._on_random)
        filter_box.append(random_btn)

        sidebar_box.append(filter_box)

        # Recipe list
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.add_css_class("navigation-sidebar")
        self.listbox.connect("row-selected", self._on_recipe_selected)
        scrolled.set_child(self.listbox)
        sidebar_box.append(scrolled)

        # Status label
        self.status_label = Gtk.Label(xalign=0)
        self.status_label.add_css_class("dim-label")
        self.status_label.set_margin_start(8)
        self.status_label.set_margin_bottom(4)
        self.status_label.set_margin_top(4)
        sidebar_box.append(self.status_label)

        sidebar_page.set_child(sidebar_box)

        # --- Content ---
        content_page = Adw.NavigationPage(title=_("Recipe"))
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        content_header = Adw.HeaderBar()

        # Action buttons in content header
        edit_btn = Gtk.Button(icon_name="document-edit-symbolic", tooltip_text=_("Edit"))
        edit_btn.connect("clicked", self._on_edit_recipe)
        content_header.pack_end(edit_btn)

        delete_btn = Gtk.Button(icon_name="user-trash-symbolic", tooltip_text=_("Delete"))
        delete_btn.connect("clicked", self._on_delete_recipe)
        content_header.pack_end(delete_btn)

        self.fav_btn = Gtk.Button(icon_name="non-starred-symbolic", tooltip_text=_("Toggle Favorite"))
        self.fav_btn.connect("clicked", self._on_toggle_favorite)
        content_header.pack_end(self.fav_btn)

        content_box.append(content_header)

        self.recipe_view = RecipeViewWidget()
        content_box.append(self.recipe_view)

        content_page.set_child(content_box)

        self.split_view.set_sidebar(sidebar_page)
        self.split_view.set_content(content_page)

        self.set_content(self.split_view)

    def _setup_actions(self):
        # Keyboard shortcuts
        app = self.get_application()
        app.set_accels_for_action("win.add", ["<Control>n"])

    def _load_recipes(self, select_id=None):
        self.recipes = self.store.get_all()
        if self._filter_favorites:
            self.recipes = [r for r in self.recipes if r.favorite]

        # Clear listbox
        while True:
            row = self.listbox.get_row_at_index(0)
            if row is None:
                break
            self.listbox.remove(row)

        select_row = None
        for i, r in enumerate(self.recipes):
            row_widget = RecipeRow(r)
            self.listbox.append(row_widget)
            if select_id and r.id == select_id:
                select_row = i

        count = len(self.recipes)
        if self._filter_favorites:
            self.status_label.set_text(_("{count} favorites").format(count=count))
        else:
            self.status_label.set_text(_("{count} recipes").format(count=count))

        if select_row is not None:
            row = self.listbox.get_row_at_index(select_row)
            if row:
                self.listbox.select_row(row)
        elif count > 0:
            self.listbox.select_row(self.listbox.get_row_at_index(0))

    def _get_selected_recipe(self):
        row = self.listbox.get_selected_row()
        if row is None:
            return None
        child = row.get_child()
        if child and hasattr(child, "recipe_id"):
            return self.store.get(child.recipe_id)
        return None

    def _on_recipe_selected(self, listbox, row):
        if row is None:
            return
        child = row.get_child()
        if child and hasattr(child, "recipe_id"):
            recipe = self.store.get(child.recipe_id)
            if recipe:
                self.recipe_view.show_recipe(recipe)
                icon = "starred-symbolic" if recipe.favorite else "non-starred-symbolic"
                self.fav_btn.set_icon_name(icon)

    def _on_search(self, entry):
        text = entry.get_text().strip()
        if not text:
            self._load_recipes()
            return
        try:
            self.recipes = self.store.search(text)
        except Exception:
            self.recipes = []

        while True:
            row = self.listbox.get_row_at_index(0)
            if row is None:
                break
            self.listbox.remove(row)

        for r in self.recipes:
            self.listbox.append(RecipeRow(r))

        self.status_label.set_text(
            _("{count} results for '{query}'").format(count=len(self.recipes), query=text)
        )
        if self.recipes:
            self.listbox.select_row(self.listbox.get_row_at_index(0))

    def _on_add_recipe(self, *args):
        dialog = RecipeEditorDialog(self)
        dialog.connect("saved", self._on_editor_saved)
        dialog.present(self)

    def _on_edit_recipe(self, *args):
        recipe = self._get_selected_recipe()
        if not recipe:
            return
        dialog = RecipeEditorDialog(self, recipe=recipe)
        dialog.connect("saved", self._on_editor_saved)
        dialog.present(self)

    def _on_editor_saved(self, dialog, recipe_id):
        self._load_recipes(select_id=recipe_id)

    def _on_delete_recipe(self, *args):
        recipe = self._get_selected_recipe()
        if not recipe:
            return

        dialog = Adw.AlertDialog(
            heading=_("Delete Recipe"),
            body=_("Delete '{name}'?").format(name=recipe.name),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("delete", _("Delete"))
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.connect("response", self._on_delete_response, recipe.id)
        dialog.present(self)

    def _on_delete_response(self, dialog, response, recipe_id):
        if response == "delete":
            self.store.delete(recipe_id)
            self._load_recipes()

    def _on_random(self, *args):
        recipe = self.store.random()
        if recipe:
            self.recipe_view.show_recipe(recipe)
            # Select in list
            for i in range(len(self.recipes)):
                row = self.listbox.get_row_at_index(i)
                if row and row.get_child() and row.get_child().recipe_id == recipe.id:
                    self.listbox.select_row(row)
                    break
            self.status_label.set_text(_("Random pick: {name}").format(name=recipe.name))

    def _on_toggle_favorite(self, *args):
        recipe = self._get_selected_recipe()
        if not recipe:
            return
        recipe.favorite = not recipe.favorite
        self.store.save(recipe)
        self._load_recipes(select_id=recipe.id)

    def _on_filter_favorites(self, btn):
        self._filter_favorites = btn.get_active()
        self._load_recipes()
