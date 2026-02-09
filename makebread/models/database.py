"""SQLite database manager for makeBread."""

import sqlite3
import json
import os
from pathlib import Path
from typing import Optional

def get_db_path() -> Path:
    """Get the database file path (XDG-compatible)."""
    data_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "makebread"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "recipes.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a database connection."""
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize the database schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT 'white',
            loaf_size TEXT DEFAULT '2lb',
            prep_time_min INTEGER DEFAULT 0,
            total_time_min INTEGER DEFAULT 0,
            machine_brand TEXT DEFAULT '',
            machine_model TEXT DEFAULT '',
            machine_program TEXT DEFAULT '',
            crust_setting TEXT DEFAULT 'medium',
            source_url TEXT DEFAULT '',
            source_name TEXT DEFAULT '',
            author TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            rating INTEGER DEFAULT 0,
            times_made INTEGER DEFAULT 0,
            favorite INTEGER DEFAULT 0,
            image_path TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            sort_order INTEGER DEFAULT 0,
            amount TEXT DEFAULT '',
            unit TEXT DEFAULT '',
            name TEXT NOT NULL,
            group_name TEXT DEFAULT '',
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS instructions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS recipes_fts USING fts5(
            name, description, tags, notes,
            content='recipes',
            content_rowid='id'
        );

        CREATE TRIGGER IF NOT EXISTS recipes_ai AFTER INSERT ON recipes BEGIN
            INSERT INTO recipes_fts(rowid, name, description, tags, notes)
            VALUES (new.id, new.name, new.description, new.tags, new.notes);
        END;

        CREATE TRIGGER IF NOT EXISTS recipes_ad AFTER DELETE ON recipes BEGIN
            INSERT INTO recipes_fts(recipes_fts, rowid, name, description, tags, notes)
            VALUES ('delete', old.id, old.name, old.description, old.tags, old.notes);
        END;

        CREATE TRIGGER IF NOT EXISTS recipes_au AFTER UPDATE ON recipes BEGIN
            INSERT INTO recipes_fts(recipes_fts, rowid, name, description, tags, notes)
            VALUES ('delete', old.id, old.name, old.description, old.tags, old.notes);
            INSERT INTO recipes_fts(rowid, name, description, tags, notes)
            VALUES (new.id, new.name, new.description, new.tags, new.notes);
        END;
    """)
    conn.commit()
