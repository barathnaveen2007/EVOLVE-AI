import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "evolve_ai.db"

def get_connection():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with get_connection() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY CHECK(id=1),
            name TEXT, occupation TEXT, skills TEXT, weekly_hours REAL,
            preferences TEXT, constraints TEXT, about TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        INSERT OR IGNORE INTO profiles(id, name, weekly_hours) VALUES(1, '', 5);
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, description TEXT, target_date TEXT,
            status TEXT DEFAULT 'Active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL, scenario_key TEXT, scenario_name TEXT,
            score INTEGER, forecast_text TEXT, assumptions TEXT,
            confidence INTEGER, weekly_hours REAL, consistency INTEGER,
            practical INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(goal_id) REFERENCES goals(id)
        );
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER NOT NULL, title TEXT, duration_days INTEGER,
            measure TEXT, target_value REAL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prediction_id) REFERENCES predictions(id)
        );
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL, value REAL, notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(experiment_id) REFERENCES experiments(id)
        );
        """)
