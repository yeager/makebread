# Changelog

All notable changes to makeBread will be documented in this file.

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
