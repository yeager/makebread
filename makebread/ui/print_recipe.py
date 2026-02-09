"""Print recipe with nice formatting."""

from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QTextDocument

from makebread.i18n import _
from makebread.models.recipe import Recipe


def print_recipe(recipe: Recipe, parent: QWidget = None):
    """Open print dialog and print a nicely formatted recipe."""
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    dialog = QPrintDialog(printer, parent)
    dialog.setWindowTitle(_("Print Recipe"))

    if dialog.exec():
        doc = QTextDocument()
        doc.setHtml(_recipe_print_html(recipe))
        doc.print_(printer)


def _recipe_print_html(r: Recipe) -> str:
    """Generate print-optimized HTML."""
    ingredients = ""
    for ing in r.ingredients:
        amt = f"{ing.amount} {ing.unit}".strip()
        if amt:
            ingredients += f"<tr><td style='padding:2px 12px 2px 0;white-space:nowrap;'><b>{amt}</b></td><td>{ing.name}</td></tr>"
        else:
            ingredients += f"<tr><td></td><td>{ing.name}</td></tr>"

    steps = ""
    for inst in r.instructions:
        steps += f"<li style='margin-bottom:6px;'>{inst.text}</li>"

    meta = []
    if r.loaf_size:
        meta.append(f"{_('Loaf')}: {r.loaf_size}")
    if r.machine_program:
        meta.append(f"{_('Program')}: {r.machine_program}")
    if r.crust_setting:
        meta.append(f"{_('Crust')}: {r.crust_setting}")
    if r.machine_brand or r.machine_model:
        meta.append(f"{_('Machine')}: {r.machine_brand} {r.machine_model}".strip())

    return f"""
    <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto;">
        <h1 style="border-bottom: 2px solid #333; padding-bottom: 8px;">{r.name}</h1>
        {f'<p style="font-style:italic; color:#555;">{r.description}</p>' if r.description else ''}
        <p style="font-size:0.9em; color:#777;">{'  |  '.join(meta)}</p>

        <h2 style="font-size:1.1em; margin-top:20px;">{_("Ingredients")}</h2>
        <table style="border-collapse:collapse;">{ingredients}</table>

        <h2 style="font-size:1.1em; margin-top:20px;">{_("Instructions")}</h2>
        <ol>{steps}</ol>

        {f'<h2 style="font-size:1.1em;">{_("Notes")}</h2><p>{r.notes}</p>' if r.notes else ''}

        <hr style="margin-top:30px;">
        <p style="font-size:0.8em; color:#999; text-align:center;">makeBread 🍞</p>
    </div>
    """
