"""Internationalization support using gettext."""

import gettext
import locale
import os
from pathlib import Path

_LOCALE_DIR = Path(__file__).parent.parent / "resources" / "locale"
_DOMAIN = "makebread"

# Initialize with system locale, fall back to English
try:
    lang = locale.getdefaultlocale()[0] or "en"
except ValueError:
    lang = "en"

_translation = gettext.translation(
    _DOMAIN,
    localedir=str(_LOCALE_DIR),
    languages=[lang, "en"],
    fallback=True,
)

# Export the gettext function as _()
_ = _translation.gettext
ngettext = _translation.ngettext
