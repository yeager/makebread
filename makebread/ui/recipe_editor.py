"""Recipe editor dialog — GTK4/Adwaita."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, GObject

from makebread.i18n import _
from makebread.models.recipe import Recipe, Ingredient, Instruction


CATEGORIES = [
    "white", "wheat", "whole grain", "rye", "sourdough",
    "sweet", "gluten-free", "fruit", "cheese", "herb",
    "dough only", "other"
]

LOAF_SIZES = ["1lb", "1.5lb", "2lb", "2.5lb", "3lb"]

PROGRAMS = [
    "Basic/White", "Whole Wheat", "French", "Sweet",
    "Quick/Rapid", "Dough", "Jam", "Cake",
    "Gluten-Free", "Homemade/Programmable", "Other"
]

CRUST_SETTINGS = ["light", "medium", "dark"]


class RecipeEditorDialog(Adw.Dialog):
    __gsignals__ = {
        "saved": (GObject.SignalFlags.RUN_LAST, None, (int,)),
    }

    def __init__(self, window, recipe: Recipe = None):
        super().__init__()
        self.window = window
        self.store = window.store
        self.recipe = recipe
        self.set_title(_("Edit Recipe") if recipe else _("New Recipe"))
        self.set_content_width(650)
        self.set_content_height(600)

        self._ingredient_rows = []
        self._instruction_rows = []

        self._setup_ui()
        if recipe:
            self._populate(recipe)

    def _setup_ui(self):
        toolbarview = Adw.ToolbarView()

        # Header
        header = Adw.HeaderBar()
        cancel_btn = Gtk.Button(label=_("Cancel"))
        cancel_btn.connect("clicked", lambda *_: self.close())
        header.pack_start(cancel_btn)

        save_btn = Gtk.Button(label=_("Save"))
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._on_save)
        header.pack_end(save_btn)

        toolbarview.add_top_bar(header)

        # Notebook (ViewStack)
        stack = Adw.ViewStack()

        # --- Basic Info page ---
        basic_page = self._build_basic_page()
        stack.add_titled(basic_page, "basic", _("Basic Info"))

        # --- Ingredients page ---
        ing_page = self._build_ingredients_page()
        stack.add_titled(ing_page, "ingredients", _("Ingredients"))

        # --- Instructions page ---
        inst_page = self._build_instructions_page()
        stack.add_titled(inst_page, "instructions", _("Instructions"))

        # --- Notes page ---
        notes_page = self._build_notes_page()
        stack.add_titled(notes_page, "notes", _("Notes"))

        # Switcher bar
        switcher = Adw.ViewSwitcherBar(stack=stack, reveal=True)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(stack)
        main_box.append(switcher)

        toolbarview.set_content(main_box)
        self.set_child(toolbarview)

    def _build_basic_page(self):
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        clamp = Adw.Clamp(maximum_size=600)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        clamp.set_margin_top(12)
        clamp.set_margin_bottom(12)

        group = Adw.PreferencesGroup(title=_("Recipe Details"))

        self.name_row = Adw.EntryRow(title=_("Name"))
        group.add(self.name_row)

        self.desc_row = Adw.EntryRow(title=_("Description"))
        group.add(self.desc_row)

        self.category_row = Adw.ComboRow(title=_("Category"))
        cat_model = Gtk.StringList.new(CATEGORIES)
        self.category_row.set_model(cat_model)
        group.add(self.category_row)

        self.loaf_row = Adw.ComboRow(title=_("Loaf Size"))
        loaf_model = Gtk.StringList.new(LOAF_SIZES)
        self.loaf_row.set_model(loaf_model)
        group.add(self.loaf_row)

        self.program_row = Adw.ComboRow(title=_("Program"))
        prog_model = Gtk.StringList.new(PROGRAMS)
        self.program_row.set_model(prog_model)
        group.add(self.program_row)

        self.crust_row = Adw.ComboRow(title=_("Crust"))
        crust_model = Gtk.StringList.new(CRUST_SETTINGS)
        self.crust_row.set_model(crust_model)
        group.add(self.crust_row)

        self.brand_row = Adw.EntryRow(title=_("Machine Brand"))
        group.add(self.brand_row)

        self.model_row = Adw.EntryRow(title=_("Machine Model"))
        group.add(self.model_row)

        self.author_row = Adw.EntryRow(title=_("Author"))
        group.add(self.author_row)

        self.source_row = Adw.EntryRow(title=_("Source URL"))
        group.add(self.source_row)

        self.tags_row = Adw.EntryRow(title=_("Tags (comma separated)"))
        group.add(self.tags_row)

        clamp.set_child(group)
        scrolled.set_child(clamp)
        return scrolled

    def _build_ingredients_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        self.ing_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        self.ing_list.add_css_class("boxed-list")
        self.ing_list.set_margin_start(12)
        self.ing_list.set_margin_end(12)
        self.ing_list.set_margin_top(12)
        scrolled.set_child(self.ing_list)
        box.append(scrolled)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8,
                          halign=Gtk.Align.CENTER)
        btn_box.set_margin_top(8)
        btn_box.set_margin_bottom(8)

        add_btn = Gtk.Button(label=_("+ Add Ingredient"))
        add_btn.connect("clicked", lambda *_: self._add_ingredient_row())
        btn_box.append(add_btn)

        box.append(btn_box)
        return box

    def _add_ingredient_row(self, amount="", unit="", name="", group=""):
        row = Adw.ActionRow(title=name or _("New ingredient"))
        
        # Amount
        amount_entry = Gtk.Entry(placeholder_text=_("Amount"), text=amount, width_chars=6)
        amount_entry.set_valign(Gtk.Align.CENTER)
        row.add_prefix(amount_entry)

        # Unit
        unit_entry = Gtk.Entry(placeholder_text=_("Unit"), text=unit, width_chars=6)
        unit_entry.set_valign(Gtk.Align.CENTER)
        row.add_prefix(unit_entry)

        # Name
        name_entry = Gtk.Entry(placeholder_text=_("Ingredient"), text=name, hexpand=True)
        name_entry.set_valign(Gtk.Align.CENTER)
        name_entry.connect("changed", lambda e: row.set_title(e.get_text() or _("New ingredient")))
        row.add_suffix(name_entry)

        # Remove button
        rm_btn = Gtk.Button(icon_name="list-remove-symbolic", valign=Gtk.Align.CENTER)
        rm_btn.add_css_class("flat")
        rm_btn.connect("clicked", lambda *_: self._remove_ing_row(row))
        row.add_suffix(rm_btn)

        self.ing_list.append(row)
        self._ingredient_rows.append((row, amount_entry, unit_entry, name_entry))

    def _remove_ing_row(self, row):
        self._ingredient_rows = [(r, a, u, n) for r, a, u, n in self._ingredient_rows if r != row]
        self.ing_list.remove(row)

    def _build_instructions_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        self.inst_list = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        self.inst_list.add_css_class("boxed-list")
        self.inst_list.set_margin_start(12)
        self.inst_list.set_margin_end(12)
        self.inst_list.set_margin_top(12)
        scrolled.set_child(self.inst_list)
        box.append(scrolled)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8,
                          halign=Gtk.Align.CENTER)
        btn_box.set_margin_top(8)
        btn_box.set_margin_bottom(8)

        add_btn = Gtk.Button(label=_("+ Add Step"))
        add_btn.connect("clicked", lambda *_: self._add_instruction_row())
        btn_box.append(add_btn)

        box.append(btn_box)
        return box

    def _add_instruction_row(self, text=""):
        step_num = len(self._instruction_rows) + 1
        row = Adw.ActionRow(title=f"{_('Step')} {step_num}")

        text_entry = Gtk.Entry(placeholder_text=_("Instruction"), text=text, hexpand=True)
        text_entry.set_valign(Gtk.Align.CENTER)
        row.add_suffix(text_entry)

        rm_btn = Gtk.Button(icon_name="list-remove-symbolic", valign=Gtk.Align.CENTER)
        rm_btn.add_css_class("flat")
        rm_btn.connect("clicked", lambda *_: self._remove_inst_row(row))
        row.add_suffix(rm_btn)

        self.inst_list.append(row)
        self._instruction_rows.append((row, text_entry))

    def _remove_inst_row(self, row):
        self._instruction_rows = [(r, t) for r, t in self._instruction_rows if r != row]
        self.inst_list.remove(row)

    def _build_notes_page(self):
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        self.notes_view = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        self.notes_view.set_margin_start(12)
        self.notes_view.set_margin_end(12)
        self.notes_view.set_margin_top(12)
        self.notes_view.set_margin_bottom(12)
        scrolled.set_child(self.notes_view)
        return scrolled

    def _populate(self, r: Recipe):
        self.name_row.set_text(r.name)
        self.desc_row.set_text(r.description)

        # Set combo rows
        try:
            idx = CATEGORIES.index(r.category)
            self.category_row.set_selected(idx)
        except ValueError:
            pass
        try:
            idx = LOAF_SIZES.index(r.loaf_size)
            self.loaf_row.set_selected(idx)
        except ValueError:
            pass
        try:
            idx = PROGRAMS.index(r.machine_program)
            self.program_row.set_selected(idx)
        except ValueError:
            pass
        try:
            idx = CRUST_SETTINGS.index(r.crust_setting)
            self.crust_row.set_selected(idx)
        except ValueError:
            pass

        self.brand_row.set_text(r.machine_brand)
        self.model_row.set_text(r.machine_model)
        self.author_row.set_text(r.author)
        self.source_row.set_text(r.source_url)
        self.tags_row.set_text(", ".join(r.tags))
        self.notes_view.get_buffer().set_text(r.notes)

        for ing in r.ingredients:
            self._add_ingredient_row(ing.amount, ing.unit, ing.name, ing.group_name)

        for inst in r.instructions:
            self._add_instruction_row(inst.text)

    def _on_save(self, *args):
        name = self.name_row.get_text().strip()
        if not name:
            return

        tags_text = self.tags_row.get_text().strip()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()] if tags_text else []

        buf = self.notes_view.get_buffer()
        notes = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)

        def get_combo_text(combo_row, options):
            idx = combo_row.get_selected()
            if 0 <= idx < len(options):
                return options[idx]
            return options[0] if options else ""

        recipe = Recipe(
            name=name,
            description=self.desc_row.get_text().strip(),
            category=get_combo_text(self.category_row, CATEGORIES),
            loaf_size=get_combo_text(self.loaf_row, LOAF_SIZES),
            machine_program=get_combo_text(self.program_row, PROGRAMS),
            crust_setting=get_combo_text(self.crust_row, CRUST_SETTINGS),
            machine_brand=self.brand_row.get_text().strip(),
            machine_model=self.model_row.get_text().strip(),
            author=self.author_row.get_text().strip(),
            source_url=self.source_row.get_text().strip(),
            notes=notes.strip(),
            tags=tags,
        )
        if self.recipe:
            recipe.id = self.recipe.id
            recipe.favorite = self.recipe.favorite

        # Ingredients
        for row, amount_e, unit_e, name_e in self._ingredient_rows:
            ing_name = name_e.get_text().strip()
            if not ing_name:
                continue
            recipe.ingredients.append(Ingredient(
                amount=amount_e.get_text().strip(),
                unit=unit_e.get_text().strip(),
                name=ing_name,
                sort_order=len(recipe.ingredients),
            ))

        # Instructions
        for i, (row, text_e) in enumerate(self._instruction_rows):
            text = text_e.get_text().strip()
            if not text:
                continue
            recipe.instructions.append(Instruction(step_number=i + 1, text=text))

        rid = self.store.save(recipe)
        self.emit("saved", rid)
        self.close()
