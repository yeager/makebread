"""Internationalization support using gettext."""

import gettext
import locale
import os

_DOMAIN = "makebread"

# Try system locale dir first, then bundled
_SYSTEM_LOCALE = "/usr/share/locale"
_BUNDLED_LOCALE = os.path.join(os.path.dirname(__file__), "..", "resources", "locale")

# Set up locale from environment (LANG, LC_ALL, etc.)
try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

# Bind domain to system locale dir
locale.bindtextdomain(_DOMAIN, _SYSTEM_LOCALE)
locale.textdomain(_DOMAIN)
gettext.bindtextdomain(_DOMAIN, _SYSTEM_LOCALE)
gettext.textdomain(_DOMAIN)

# Use gettext module
_ = gettext.gettext
ngettext = gettext.ngettext
