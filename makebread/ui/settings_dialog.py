"""Settings for makeBread — GTK4/Adwaita (uses GLib KeyFile)."""

import os
from pathlib import Path

from makebread.i18n import _
from makebread.utils.units import SYSTEM_US, SYSTEM_METRIC, SYSTEM_IMPERIAL


def _config_path() -> Path:
    config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "makebread"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "settings.ini"


def get_settings() -> dict:
    """Read settings as a simple dict."""
    defaults = {
        "unit_system": SYSTEM_US,
        "auto_convert_units": True,
        "show_machine_info": True,
        "show_category_badges": True,
    }
    path = _config_path()
    if not path.exists():
        return defaults

    import configparser
    cp = configparser.ConfigParser()
    cp.read(str(path))
    if "makebread" in cp:
        s = cp["makebread"]
        defaults["unit_system"] = s.get("unit_system", SYSTEM_US)
        defaults["auto_convert_units"] = s.getboolean("auto_convert_units", True)
        defaults["show_machine_info"] = s.getboolean("show_machine_info", True)
        defaults["show_category_badges"] = s.getboolean("show_category_badges", True)
    return defaults


def save_settings(settings: dict):
    import configparser
    cp = configparser.ConfigParser()
    cp["makebread"] = {k: str(v) for k, v in settings.items()}
    with open(_config_path(), "w") as f:
        cp.write(f)


def get_unit_system() -> str:
    return get_settings()["unit_system"]
