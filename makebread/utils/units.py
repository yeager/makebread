"""Unit conversion for recipe measurements."""

from fractions import Fraction
from makebread.i18n import _

# Unit systems
SYSTEM_US = "us"
SYSTEM_METRIC = "metric"
SYSTEM_IMPERIAL = "imperial"

SYSTEMS = {
    SYSTEM_US: _("US (cups, oz, °F)"),
    SYSTEM_METRIC: _("Metric (dl, g, °C)"),
    SYSTEM_IMPERIAL: _("Imperial (fl oz, oz, °C)"),
}

# Canonical unit names for display
UNIT_NAMES = {
    SYSTEM_US: {
        "cup": _("cup"), "cups": _("cups"),
        "tbsp": _("tbsp"), "tsp": _("tsp"),
        "oz": _("oz"), "lb": _("lb"),
        "fl oz": _("fl oz"),
    },
    SYSTEM_METRIC: {
        "dl": _("dl"), "ml": _("ml"), "l": _("l"),
        "g": _("g"), "kg": _("kg"),
        "tbsp": _("tbsp"), "tsp": _("tsp"),
    },
    SYSTEM_IMPERIAL: {
        "fl oz": _("fl oz"), "ml": _("ml"),
        "oz": _("oz"), "lb": _("lb"),
        "tbsp": _("tbsp"), "tsp": _("tsp"),
    },
}

# Conversion factors to metric base (ml for volume, g for weight)
TO_ML = {
    "cup": 236.588, "cups": 236.588,
    "tbsp": 14.787, "tbs": 14.787, "tablespoon": 14.787, "tablespoons": 14.787,
    "tsp": 4.929, "teaspoon": 4.929, "teaspoons": 4.929,
    "fl oz": 29.574, "fluid ounce": 29.574, "fluid ounces": 29.574,
    "ml": 1.0, "milliliter": 1.0, "milliliters": 1.0,
    "dl": 100.0, "deciliter": 100.0, "deciliters": 100.0,
    "l": 1000.0, "liter": 1000.0, "liters": 1000.0,
}

TO_GRAMS = {
    "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495,
    "lb": 453.592, "lbs": 453.592, "pound": 453.592, "pounds": 453.592,
    "g": 1.0, "gram": 1.0, "grams": 1.0,
    "kg": 1000.0, "kilogram": 1000.0, "kilograms": 1000.0,
}

# Small units that stay the same across systems
KEEP_UNITS = {"tsp", "teaspoon", "teaspoons", "tbsp", "tbs", "tablespoon", "tablespoons",
              "pinch", "dash", "piece", "pieces", "slice", "slices",
              "clove", "cloves", "packet", "packets", "package", "packages",
              "envelope", "envelopes", "can", "cans"}


def parse_amount(amount_str: str) -> float:
    """Parse an amount string like '1 1/2' or '2/3' to a float."""
    if not amount_str or not amount_str.strip():
        return 0.0
    parts = amount_str.strip().split()
    total = 0.0
    for part in parts:
        try:
            total += float(Fraction(part))
        except (ValueError, ZeroDivisionError):
            try:
                total += float(part)
            except ValueError:
                return 0.0
    return total


def format_amount(value: float) -> str:
    """Format a float to a nice display string (fractions for small values)."""
    if value == 0:
        return ""
    if value == int(value):
        return str(int(value))
    # Try common fractions
    for denom in [2, 3, 4, 8]:
        numer = round(value * denom)
        if abs(numer / denom - value) < 0.01:
            whole = numer // denom
            frac = numer % denom
            if frac == 0:
                return str(whole)
            if whole == 0:
                return f"{frac}/{denom}"
            return f"{whole} {frac}/{denom}"
    # Fallback to decimal
    return f"{value:.1f}"


def convert_unit(amount: float, from_unit: str, to_system: str) -> tuple[float, str]:
    """
    Convert an amount from one unit to the target system.
    Returns (new_amount, new_unit).
    """
    unit_lower = from_unit.lower().strip()

    # Keep small/non-convertible units as-is
    if unit_lower in KEEP_UNITS or not unit_lower:
        return amount, from_unit

    # Volume conversions
    if unit_lower in TO_ML:
        ml = amount * TO_ML[unit_lower]
        if to_system == SYSTEM_METRIC:
            if ml >= 1000:
                return ml / 1000, "l"
            if ml >= 100:
                return ml / 100, "dl"
            return ml, "ml"
        elif to_system == SYSTEM_US:
            if ml >= 236:
                return ml / 236.588, "cups"
            if ml >= 14.5:
                return ml / 14.787, "tbsp"
            return ml / 4.929, "tsp"
        elif to_system == SYSTEM_IMPERIAL:
            if ml >= 28:
                return ml / 29.574, "fl oz"
            if ml >= 14.5:
                return ml / 14.787, "tbsp"
            return ml / 4.929, "tsp"

    # Weight conversions
    if unit_lower in TO_GRAMS:
        grams = amount * TO_GRAMS[unit_lower]
        if to_system == SYSTEM_METRIC:
            if grams >= 1000:
                return grams / 1000, "kg"
            return grams, "g"
        elif to_system in (SYSTEM_US, SYSTEM_IMPERIAL):
            if grams >= 453:
                return grams / 453.592, "lb"
            return grams / 28.3495, "oz"

    # Unknown unit — return as-is
    return amount, from_unit


def convert_ingredient(amount_str: str, unit: str, to_system: str) -> tuple[str, str]:
    """
    Convert an ingredient's amount and unit to the target system.
    Returns (new_amount_str, new_unit).
    """
    amount = parse_amount(amount_str)
    if amount == 0:
        return amount_str, unit

    new_amount, new_unit = convert_unit(amount, unit, to_system)
    return format_amount(new_amount), new_unit
