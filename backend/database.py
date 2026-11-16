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
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'  -- 'customer' or 'owner'
        );

        -- Business hours for each day of the week (0 = Monday ... 6 = Sunday)
        CREATE TABLE IF NOT EXISTS business_hours (
            day_of_week INTEGER PRIMARY KEY,
            open_time TEXT NOT NULL,   -- "09:00"
            close_time TEXT NOT NULL   -- "17:00"
        );

        -- UNIQUE(date, time) is what stops double bookings
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            date TEXT NOT NULL,        -- "2026-11-20"
            time TEXT NOT NULL,        -- "10:30"
            UNIQUE(date, time)
        );
        """
    )
    conn.commit()
    conn.close()
