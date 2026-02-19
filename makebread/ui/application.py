"""GTK4/Adwaita Application class."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio, GLib
from pathlib import Path

from makebread.models.database import get_connection, init_db
from makebread.models.recipe import RecipeStore
from makebread.utils.importer import import_json
from makebread.i18n import _


class MakeBreadApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="io.github.yeager.makebread",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.store = None

    def do_activate(self):
        # Init DB
        conn = get_connection()
        init_db(conn)
        self.store = RecipeStore(conn)

        # Seed on first run
        if not self.store.get_all():
            seed_file = Path(__file__).parent.parent.parent / "data" / "seed_recipes.json"
            if seed_file.exists():
                count = import_json(seed_file, self.store)
                print(f"Imported {count} seed recipes.")

        win = self.props.active_window
        if not win:
            from makebread.ui.main_window import MainWindow
            win = MainWindow(application=self, store=self.store)
        win.present()

    def do_startup(self):
        Adw.Application.do_startup(self)
        self._setup_actions()

    def _setup_actions(self):
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Control>q"])

    def _on_about(self, action, param):
        win = self.props.active_window
        dialog = Adw.AboutDialog(
            application_name="makeBread",
            application_icon="io.github.yeager.makebread",
            version="0.4.0",
            developer_name="Daniel Nylander",
            developers=["Daniel Nylander <daniel@danielnylander.se>"],
            copyright="© 2026 Daniel Nylander",
            license_type=Gtk.License.GPL_3_0,
            website="https://github.com/yeager/makebread",
            issue_url="https://github.com/yeager/makebread/issues",
            comments=_("Bread Machine Recipe Manager"),
        )
        dialog.present(win)
