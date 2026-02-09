"""Recipe data model and CRUD operations."""

import json
import random
import sqlite3
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Ingredient:
    name: str
    amount: str = ""
    unit: str = ""
    group_name: str = ""
    sort_order: int = 0


@dataclass
class Instruction:
    step_number: int
    text: str


@dataclass
class Recipe:
    name: str
    description: str = ""
    category: str = "white"
    loaf_size: str = "2lb"
    prep_time_min: int = 0
    total_time_min: int = 0
    machine_brand: str = ""
    machine_model: str = ""
    machine_program: str = ""
    crust_setting: str = "medium"
    source_url: str = ""
    source_name: str = ""
    author: str = ""
    notes: str = ""
    tags: list[str] = field(default_factory=list)
    rating: int = 0
    times_made: int = 0
    favorite: bool = False
    image_path: str = ""
    ingredients: list[Ingredient] = field(default_factory=list)
    instructions: list[Instruction] = field(default_factory=list)
    id: Optional[int] = None


class RecipeStore:
    """CRUD operations for recipes."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def save(self, recipe: Recipe) -> int:
        """Insert or update a recipe. Returns the recipe id."""
        tags_json = json.dumps(recipe.tags)
        if recipe.id is None:
            cur = self.conn.execute("""
                INSERT INTO recipes (name, description, category, loaf_size,
                    prep_time_min, total_time_min, machine_brand, machine_model,
                    machine_program, crust_setting, source_url, source_name,
                    author, notes, tags, rating, times_made, favorite, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (recipe.name, recipe.description, recipe.category, recipe.loaf_size,
                  recipe.prep_time_min, recipe.total_time_min, recipe.machine_brand,
                  recipe.machine_model, recipe.machine_program, recipe.crust_setting,
                  recipe.source_url, recipe.source_name, recipe.author, recipe.notes,
                  tags_json, recipe.rating, recipe.times_made, int(recipe.favorite),
                  recipe.image_path))
            recipe.id = cur.lastrowid
        else:
            self.conn.execute("""
                UPDATE recipes SET name=?, description=?, category=?, loaf_size=?,
                    prep_time_min=?, total_time_min=?, machine_brand=?, machine_model=?,
                    machine_program=?, crust_setting=?, source_url=?, source_name=?,
                    author=?, notes=?, tags=?, rating=?, times_made=?, favorite=?,
                    image_path=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (recipe.name, recipe.description, recipe.category, recipe.loaf_size,
                  recipe.prep_time_min, recipe.total_time_min, recipe.machine_brand,
                  recipe.machine_model, recipe.machine_program, recipe.crust_setting,
                  recipe.source_url, recipe.source_name, recipe.author, recipe.notes,
                  tags_json, recipe.rating, recipe.times_made, int(recipe.favorite),
                  recipe.image_path, recipe.id))
            # Clear old ingredients/instructions
            self.conn.execute("DELETE FROM ingredients WHERE recipe_id=?", (recipe.id,))
            self.conn.execute("DELETE FROM instructions WHERE recipe_id=?", (recipe.id,))

        # Save ingredients
        for i, ing in enumerate(recipe.ingredients):
            self.conn.execute("""
                INSERT INTO ingredients (recipe_id, sort_order, amount, unit, name, group_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (recipe.id, i, ing.amount, ing.unit, ing.name, ing.group_name))

        # Save instructions
        for inst in recipe.instructions:
            self.conn.execute("""
                INSERT INTO instructions (recipe_id, step_number, text)
                VALUES (?, ?, ?)
            """, (recipe.id, inst.step_number, inst.text))

        self.conn.commit()
        return recipe.id

    def get(self, recipe_id: int) -> Optional[Recipe]:
        """Get a recipe by ID."""
        row = self.conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_recipe(row)

    def get_all(self) -> list[Recipe]:
        """Get all recipes."""
        rows = self.conn.execute("SELECT * FROM recipes ORDER BY name").fetchall()
        return [self._row_to_recipe(r) for r in rows]

    def search(self, query: str) -> list[Recipe]:
        """Full-text search recipes."""
        rows = self.conn.execute("""
            SELECT r.* FROM recipes r
            JOIN recipes_fts fts ON r.id = fts.rowid
            WHERE recipes_fts MATCH ?
            ORDER BY rank
        """, (query,)).fetchall()
        # Also search ingredients
        ing_rows = self.conn.execute("""
            SELECT DISTINCT r.* FROM recipes r
            JOIN ingredients i ON r.id = i.recipe_id
            WHERE i.name LIKE ?
        """, (f"%{query}%",)).fetchall()
        seen = {r["id"] for r in rows}
        combined = list(rows)
        for r in ing_rows:
            if r["id"] not in seen:
                combined.append(r)
        return [self._row_to_recipe(r) for r in combined]

    def random(self) -> Optional[Recipe]:
        """Get a random recipe."""
        row = self.conn.execute(
            "SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return self._row_to_recipe(row)

    def delete(self, recipe_id: int) -> None:
        """Delete a recipe."""
        self.conn.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
        self.conn.commit()

    def _row_to_recipe(self, row: sqlite3.Row) -> Recipe:
        """Convert a database row to a Recipe object."""
        recipe = Recipe(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            category=row["category"],
            loaf_size=row["loaf_size"],
            prep_time_min=row["prep_time_min"],
            total_time_min=row["total_time_min"],
            machine_brand=row["machine_brand"],
            machine_model=row["machine_model"],
            machine_program=row["machine_program"],
            crust_setting=row["crust_setting"],
            source_url=row["source_url"],
            source_name=row["source_name"],
            author=row["author"],
            notes=row["notes"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            rating=row["rating"],
            times_made=row["times_made"],
            favorite=bool(row["favorite"]),
            image_path=row["image_path"] if "image_path" in row.keys() else "",
        )
        # Load ingredients
        ing_rows = self.conn.execute(
            "SELECT * FROM ingredients WHERE recipe_id=? ORDER BY sort_order",
            (recipe.id,)
        ).fetchall()
        recipe.ingredients = [
            Ingredient(name=r["name"], amount=r["amount"], unit=r["unit"],
                       group_name=r["group_name"], sort_order=r["sort_order"])
            for r in ing_rows
        ]
        # Load instructions
        inst_rows = self.conn.execute(
            "SELECT * FROM instructions WHERE recipe_id=? ORDER BY step_number",
            (recipe.id,)
        ).fetchall()
        recipe.instructions = [
            Instruction(step_number=r["step_number"], text=r["text"])
            for r in inst_rows
        ]
        return recipe
