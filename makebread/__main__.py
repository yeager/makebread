"""makeBread application entry point."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from makebread.models.database import get_connection, init_db, get_db_path
from makebread.models.recipe import RecipeStore
from makebread.ui.main_window import MainWindow
from makebread.utils.importer import import_json


def main():
    # On macOS, set process name so menu bar shows "makeBread" not "Python"
    if sys.platform == "darwin":
        try:
            from Foundation import NSBundle
            bundle = NSBundle.mainBundle()
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            if info:
                info["CFBundleName"] = "makeBread"
        except ImportError:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("makeBread")
    app.setApplicationDisplayName("makeBread")
    app.setOrganizationName("makeBread")
    app.setDesktopFileName("makeBread")

    # Initialize database
    conn = get_connection()
    init_db(conn)
    store = RecipeStore(conn)

    # Seed with default recipes on first run
    if not store.get_all():
        seed_file = Path(__file__).parent.parent / "data" / "seed_recipes.json"
        if seed_file.exists():
            count = import_json(seed_file, store)
            print(f"Imported {count} seed recipes.")

    window = MainWindow(store)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
