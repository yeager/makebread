"""Import/export recipes as JSON."""

import json
from pathlib import Path
from makebread.models.recipe import Recipe, Ingredient, Instruction, RecipeStore


def import_json(filepath: Path, store: RecipeStore) -> int:
    """Import recipes from a JSON file. Returns count imported."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    recipes = data if isinstance(data, list) else [data]
    count = 0
    for rd in recipes:
        recipe = Recipe(
            name=rd.get("name", "Untitled"),
            description=rd.get("description", ""),
            category=rd.get("category", "white"),
            loaf_size=rd.get("loaf_size", "2lb"),
            prep_time_min=rd.get("prep_time_min", 0),
            total_time_min=rd.get("total_time_min", 0),
            machine_brand=rd.get("machine_brand", ""),
            machine_model=rd.get("machine_model", ""),
            machine_program=rd.get("machine_program", "Basic/White"),
            crust_setting=rd.get("crust_setting", "medium"),
            source_url=rd.get("source_url", ""),
            source_name=rd.get("source_name", ""),
            author=rd.get("author", ""),
            notes=rd.get("notes", ""),
            tags=rd.get("tags", []),
        )
        for ing in rd.get("ingredients", []):
            recipe.ingredients.append(Ingredient(
                name=ing.get("name", ""),
                amount=str(ing.get("amount", "")),
                unit=ing.get("unit", ""),
                group_name=ing.get("group", ""),
            ))
        for i, step in enumerate(rd.get("instructions", []), 1):
            if isinstance(step, str):
                recipe.instructions.append(Instruction(step_number=i, text=step))
            else:
                recipe.instructions.append(Instruction(
                    step_number=step.get("step", i),
                    text=step.get("text", ""),
                ))
        store.save(recipe)
        count += 1
    return count


def export_json(recipes: list[Recipe], filepath: Path) -> None:
    """Export recipes to JSON."""
    data = []
    for r in recipes:
        data.append({
            "name": r.name,
            "description": r.description,
            "category": r.category,
            "loaf_size": r.loaf_size,
            "prep_time_min": r.prep_time_min,
            "total_time_min": r.total_time_min,
            "machine_brand": r.machine_brand,
            "machine_model": r.machine_model,
            "machine_program": r.machine_program,
            "crust_setting": r.crust_setting,
            "source_url": r.source_url,
            "source_name": r.source_name,
            "author": r.author,
            "notes": r.notes,
            "tags": r.tags,
            "ingredients": [
                {"amount": i.amount, "unit": i.unit, "name": i.name, "group": i.group_name}
                for i in r.ingredients
            ],
            "instructions": [inst.text for inst in r.instructions],
        })
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
