"""Recipe display widget."""

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PySide6.QtCore import Qt

from makebread.i18n import _
from makebread.models.recipe import Recipe
from makebread.ui.settings_dialog import get_unit_system, get_settings
from makebread.utils.units import convert_ingredient, SYSTEM_US


class RecipeViewWidget(QWidget):
    """Displays a recipe in a rich text view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser)
        self.browser.setHtml(self._placeholder())

    def _placeholder(self) -> str:
        return f"""
        <div style="text-align:center; padding:60px; color:#888;">
            <h2>🍞 {_("makeBread")}</h2>
            <p>{_("Select a recipe from the list, or add a new one.")}</p>
        </div>
        """

    def show_recipe(self, recipe: Recipe):
        """Render a recipe as HTML."""
        html = self._recipe_to_html(recipe)
        self.browser.setHtml(html)

    def _recipe_to_html(self, r: Recipe) -> str:
        """Convert recipe to styled HTML."""
        # Unit conversion
        settings = get_settings()
        unit_system = settings.value("unit_system", SYSTEM_US)
        auto_convert = settings.value("auto_convert_units", True, type=bool)

        ingredients_html = ""
        current_group = None
        for ing in r.ingredients:
            if ing.group_name and ing.group_name != current_group:
                if current_group is not None:
                    ingredients_html += "</ul>"
                ingredients_html += f"<h4 style='margin:8px 0 4px;'>{ing.group_name}</h4><ul>"
                current_group = ing.group_name
            elif current_group is None:
                ingredients_html += "<ul>"
                current_group = ""

            amount = ing.amount
            unit = ing.unit
            if auto_convert and unit:
                amount, unit = convert_ingredient(amount, unit, unit_system)

            amount_str = f"{amount} {unit}".strip()
            if amount_str:
                ingredients_html += f"<li><b>{amount_str}</b> {ing.name}</li>"
            else:
                ingredients_html += f"<li>{ing.name}</li>"
        if current_group is not None:
            ingredients_html += "</ul>"

        instructions_html = "<ol>"
        for inst in r.instructions:
            instructions_html += f"<li>{inst.text}</li>"
        instructions_html += "</ol>"

        meta_parts = []
        if r.loaf_size:
            meta_parts.append(f"<b>{_('Loaf Size')}:</b> {r.loaf_size}")
        if r.machine_program:
            meta_parts.append(f"<b>{_('Program')}:</b> {r.machine_program}")
        if r.crust_setting:
            meta_parts.append(f"<b>{_('Crust')}:</b> {r.crust_setting}")
        if r.machine_brand or r.machine_model:
            machine = f"{r.machine_brand} {r.machine_model}".strip()
            meta_parts.append(f"<b>{_('Machine')}:</b> {machine}")
        if r.category:
            meta_parts.append(f"<b>{_('Category')}:</b> {r.category}")

        meta_html = " &nbsp;|&nbsp; ".join(meta_parts) if meta_parts else ""

        tags_html = ""
        if r.tags:
            tags_html = " ".join(
                f"<span style='background:#e0e0e0;padding:2px 8px;border-radius:10px;'>{t}</span>"
                for t in r.tags
            )

        source_html = ""
        if r.source_url:
            source_html = f"<p><a href='{r.source_url}'>{r.source_name or r.source_url}</a></p>"

        image_html = ""
        if r.image_path and os.path.isfile(r.image_path):
            image_html = (
                f"<div style='text-align:center;margin:12px 0;'>"
                f"<img src='file://{r.image_path}' style='max-width:100%;max-height:300px;border-radius:8px;'>"
                f"</div>"
            )

        return f"""
        <div style="font-family: sans-serif; max-width: 700px; margin: 0 auto; padding: 16px;">
            <h1 style="margin-bottom:4px;">{r.name}</h1>
            {image_html}
            {f'<p style="color:#666;">{r.description}</p>' if r.description else ''}
            <p style="font-size:0.9em; color:#888;">{meta_html}</p>
            {f'<p>{tags_html}</p>' if tags_html else ''}

            <h3>{_("Ingredients")}</h3>
            {ingredients_html}

            <h3>{_("Instructions")}</h3>
            {instructions_html}

            {f'<h3>{_("Notes")}</h3><p>{r.notes}</p>' if r.notes else ''}
            {source_html}
        </div>
        """
