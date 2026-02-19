"""Recipe display widget — GTK4/Adwaita."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Pango

from makebread.i18n import _
from makebread.models.recipe import Recipe
from makebread.utils.units import SYSTEM_US


class RecipeViewWidget(Gtk.ScrolledWindow):
    """Displays a recipe using native GTK4 widgets."""

    def __init__(self):
        super().__init__(vexpand=True, hexpand=True)
        self.clamp = Adw.Clamp(maximum_size=700)
        self.clamp.set_margin_start(16)
        self.clamp.set_margin_end(16)
        self.clamp.set_margin_top(16)
        self.clamp.set_margin_bottom(16)

        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.clamp.set_child(self.content)
        self.set_child(self.clamp)

        # Placeholder
        self._show_placeholder()

    def _show_placeholder(self):
        self._clear()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8,
                      valign=Gtk.Align.CENTER, vexpand=True)
        icon = Gtk.Label(label="🍞")
        icon.add_css_class("title-1")
        box.append(icon)
        label = Gtk.Label(label=_("Select a recipe from the list, or add a new one."))
        label.add_css_class("dim-label")
        box.append(label)
        self.content.append(box)

    def _clear(self):
        while True:
            child = self.content.get_first_child()
            if child is None:
                break
            self.content.remove(child)

    def show_recipe(self, recipe: Recipe):
        self._clear()

        # Title
        title = Gtk.Label(label=recipe.name, xalign=0, wrap=True)
        title.add_css_class("title-1")
        self.content.append(title)

        # Description
        if recipe.description:
            desc = Gtk.Label(label=recipe.description, xalign=0, wrap=True)
            desc.add_css_class("dim-label")
            self.content.append(desc)

        # Meta info
        meta_parts = []
        if recipe.loaf_size:
            meta_parts.append(f"{_('Loaf Size')}: {recipe.loaf_size}")
        if recipe.machine_program:
            meta_parts.append(f"{_('Program')}: {recipe.machine_program}")
        if recipe.crust_setting:
            meta_parts.append(f"{_('Crust')}: {recipe.crust_setting}")
        if recipe.machine_brand or recipe.machine_model:
            machine = f"{recipe.machine_brand} {recipe.machine_model}".strip()
            meta_parts.append(f"{_('Machine')}: {machine}")
        if recipe.category:
            meta_parts.append(f"{_('Category')}: {recipe.category}")

        if meta_parts:
            meta_label = Gtk.Label(label="  |  ".join(meta_parts), xalign=0, wrap=True)
            meta_label.add_css_class("dim-label")
            self.content.append(meta_label)

        # Tags
        if recipe.tags:
            tags_box = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE,
                                    max_children_per_line=10)
            tags_box.set_margin_top(4)
            for tag in recipe.tags:
                chip = Gtk.Label(label=tag)
                chip.add_css_class("caption")
                chip.set_margin_start(4)
                chip.set_margin_end(4)
                tags_box.append(chip)
            self.content.append(tags_box)

        # Ingredients
        ing_title = Gtk.Label(label=_("Ingredients"), xalign=0)
        ing_title.add_css_class("title-3")
        ing_title.set_margin_top(8)
        self.content.append(ing_title)

        current_group = None
        for ing in recipe.ingredients:
            if ing.group_name and ing.group_name != current_group:
                current_group = ing.group_name
                group_label = Gtk.Label(label=ing.group_name, xalign=0)
                group_label.add_css_class("title-4")
                group_label.set_margin_top(4)
                self.content.append(group_label)
            elif current_group is None:
                current_group = ""

            amount_str = f"{ing.amount} {ing.unit}".strip()
            if amount_str:
                text = f"• <b>{amount_str}</b>  {ing.name}"
            else:
                text = f"• {ing.name}"
            lbl = Gtk.Label(xalign=0, use_markup=True, label=text, wrap=True)
            lbl.set_margin_start(8)
            self.content.append(lbl)

        # Instructions
        inst_title = Gtk.Label(label=_("Instructions"), xalign=0)
        inst_title.add_css_class("title-3")
        inst_title.set_margin_top(8)
        self.content.append(inst_title)

        for inst in recipe.instructions:
            text = f"{inst.step_number}. {inst.text}"
            lbl = Gtk.Label(label=text, xalign=0, wrap=True)
            lbl.set_margin_start(8)
            self.content.append(lbl)

        # Notes
        if recipe.notes:
            notes_title = Gtk.Label(label=_("Notes"), xalign=0)
            notes_title.add_css_class("title-3")
            notes_title.set_margin_top(8)
            self.content.append(notes_title)
            notes_lbl = Gtk.Label(label=recipe.notes, xalign=0, wrap=True)
            notes_lbl.set_margin_start(8)
            self.content.append(notes_lbl)

        # Source
        if recipe.source_url:
            src_text = recipe.source_name or recipe.source_url
            src_lbl = Gtk.Label(xalign=0, use_markup=True,
                                label=f'<a href="{recipe.source_url}">{src_text}</a>')
            src_lbl.set_margin_top(8)
            self.content.append(src_lbl)


# Need Adw import for Clamp
from gi.repository import Adw
