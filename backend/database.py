import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );

        -- TODO: add tables for business hours and appointments
        """
    )
    conn.commit()
    conn.close()
