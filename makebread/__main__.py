"""makeBread application entry point — GTK4/Adwaita version."""

import sys
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio

from makebread.ui.application import MakeBreadApplication


def main():
    app = MakeBreadApplication()
    app.run(sys.argv)


if __name__ == "__main__":
    main()
