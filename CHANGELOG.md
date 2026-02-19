# Changelog

All notable changes to makeBread will be documented in this file.

## [0.4.0] - 2026-02-19

### Changed
- **Complete rewrite from PySide6/Qt to GTK4/Adwaita** (libadwaita)
- Modern GNOME-native UI with Adw.NavigationSplitView, Adw.Dialog, Adw.PreferencesGroup
- Uses Adw.AboutDialog (not deprecated Adw.AboutWindow)
- Adw.AlertDialog for confirmations
- Adw.ViewStack + ViewSwitcherBar for editor tabs
- Settings now use INI file (XDG_CONFIG_HOME) instead of QSettings
- Dependency changed from PySide6 to PyGObject

### Removed
- Print support (temporarily — Qt print dialog replaced, GTK4 print TBD)
- Image/photo support in editor (GTK4 file chooser portal TBD)

## [0.3.0] - 2026-02-09

### Added
- Favorite toggle button (☆/★) in toolbar (Ctrl+F)
- Favorites Only filter to show only favorite recipes
- Favorites shown with ★ prefix in recipe list

### Fixed
- Font family warning on macOS (use system font stack)

### Updated
- Swedish translations (92 strings, 100% coverage)

## [0.2.0] - 2026-02-09

### Added
- Full internationalization (i18n) support via GNU gettext
- Swedish (sv) translation — complete coverage of all UI strings
- POT template for translators (`makebread/resources/locale/makebread.pot`)
- Translation guide (`makebread/resources/locale/README.md`)

## [0.1.0] - 2026-02-09

### Added
- Recipe management (add, edit, delete) with SQLite + FTS5 database
- Full-text search across recipes and ingredients
- Random recipe picker (🎲)
- Print-ready recipe cards with clean design
- Machine and program info per recipe (brand, model, program, crust)
- Unit conversion between US, Metric, and Imperial systems
- Settings dialog (Edit → Settings, Cmd+,)
- Optional photo per recipe
- JSON import/export
- 103 built-in starter recipes
- Donate button (GitHub Sponsors + Swish)
- About dialog
- AppData/MetaInfo for Elementary AppCenter and Ubuntu Software
- Desktop entry file
- GPL-3.0-or-later license
