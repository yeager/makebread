# Translating makeBread

makeBread uses GNU gettext for internationalization.

## File Structure

```
locale/
├── makebread.pot                      # Template (source strings)
├── README.md                          # This file
└── sv/
    └── LC_MESSAGES/
        ├── makebread.po               # Swedish translation (editable)
        └── makebread.mo               # Compiled (binary, auto-generated)
```

## How to Contribute a Translation

1. Copy the template to create a new language:
   ```bash
   mkdir -p locale/<LANG>/LC_MESSAGES
   cp makebread.pot locale/<LANG>/LC_MESSAGES/makebread.po
   ```
2. Edit the `.po` file — fill in all `msgstr` fields with translations.
3. Compile:
   ```bash
   msgfmt -o locale/<LANG>/LC_MESSAGES/makebread.mo locale/<LANG>/LC_MESSAGES/makebread.po
   ```
4. Submit a pull request.

## Recommended Tools

- **[Poedit](https://poedit.net/)** — cross-platform GUI editor
- **[Lokalize](https://apps.kde.org/lokalize/)** — KDE translation tool
- **[GTranslator](https://wiki.gnome.org/Apps/Gtranslator)** — GNOME translation editor
- Any text editor works too — `.po` files are plain text

## Updating Translations

When new strings are added to the source code:

1. Regenerate `makebread.pot` (or update it manually)
2. Merge new strings into existing `.po` files:
   ```bash
   msgmerge -U locale/<LANG>/LC_MESSAGES/makebread.po makebread.pot
   ```
3. Translate the new/fuzzy entries
4. Recompile with `msgfmt`

## Current Languages

| Language | Code | Status |
|----------|------|--------|
| English  | en   | ✅ Source language |
| Svenska  | sv   | ✅ Complete |
