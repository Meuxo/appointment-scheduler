import hashlib
import secrets
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import get_db, init_db

SLOT_MINUTES = 30
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app = FastAPI(title="Appointment Scheduling System")
init_db()


# ---------- Helpers ----------

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${hashed}"


def check_password(password: str, stored: str) -> bool:
    salt, hashed = stored.split("$")
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex() == hashed


def require_owner(conn, user_id: int):
    user = conn.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user or user["role"] != "owner":
        raise HTTPException(403, "Only the business owner can do this")


# ---------- Request bodies ----------

class RegisterBody(BaseModel):
    name: str
    email: str
    password: str
    role: str = "customer"


class LoginBody(BaseModel):
    email: str
    password: str


class HoursBody(BaseModel):
    user_id: int
    day_of_week: int  # 0 = Monday ... 6 = Sunday
    open_time: str    # "09:00"
    close_time: str   # "17:00"


class BookBody(BaseModel):
    user_id: int
    date: str  # "2026-11-20"
    time: str  # "10:30"


# ---------- Requirement 1: Registration and login ----------

@app.post("/api/register")
def register(body: RegisterBody):
    if body.role not in ("customer", "owner"):
        raise HTTPException(400, "Role must be customer or owner")
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (body.name, body.email.lower(), hash_password(body.password), body.role),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(400, "That email is already registered")
    finally:
        conn.close()
    return {"message": "Account created"}


@app.post("/api/login")
def login(body: LoginBody):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (body.email.lower(),)).fetchone()
    conn.close()
    if not user or not check_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Wrong email or password")
    return {"id": user["id"], "name": user["name"], "role": user["role"]}


# ---------- Requirement 2: Business hours and open time slots ----------

@app.get("/api/hours")
def get_hours():
    conn = get_db()
    rows = conn.execute("SELECT * FROM business_hours ORDER BY day_of_week").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/hours")
def set_hours(body: HoursBody):
    conn = get_db()
    require_owner(conn, body.user_id)
    conn.execute(
        "INSERT OR REPLACE INTO business_hours (day_of_week, open_time, close_time) VALUES (?, ?, ?)",
        (body.day_of_week, body.open_time, body.close_time),
    )
    conn.commit()
    conn.close()
    return {"message": "Hours saved"}


@app.delete("/api/hours/{day_of_week}")
def close_day(day_of_week: int, user_id: int):
    conn = get_db()
    require_owner(conn, user_id)
    conn.execute("DELETE FROM business_hours WHERE day_of_week = ?", (day_of_week,))
    conn.commit()
    conn.close()
    return {"message": "Day closed"}


@app.get("/api/slots")
def open_slots(date: str):
    day = datetime.strptime(date, "%Y-%m-%d")
    conn = get_db()
    hours = conn.execute(
        "SELECT * FROM business_hours WHERE day_of_week = ?", (day.weekday(),)
    ).fetchone()
    booked = {r["time"] for r in conn.execute("SELECT time FROM appointments WHERE date = ?", (date,))}
    conn.close()
    if not hours:
        return []  # closed that day

    slots = []
    current = datetime.strptime(f"{date} {hours['open_time']}", "%Y-%m-%d %H:%M")
    close = datetime.strptime(f"{date} {hours['close_time']}", "%Y-%m-%d %H:%M")
    while current + timedelta(minutes=SLOT_MINUTES) <= close:
        time_str = current.strftime("%H:%M")
        if time_str not in booked and current > datetime.now():
            slots.append(time_str)
        current += timedelta(minutes=SLOT_MINUTES)
    return slots


# ---------- Requirement 3: Booking and cancellation ----------

@app.post("/api/appointments")
def book(body: BookBody):
    if body.time not in open_slots(body.date):
        raise HTTPException(400, "That time is not open")
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO appointments (user_id, date, time) VALUES (?, ?, ?)",
            (body.user_id, body.date, body.time),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Sorry, someone just booked that time")
    finally:
        conn.close()
    return {"message": f"Booked for {body.date} at {body.time}"}


@app.get("/api/appointments")
def my_appointments(user_id: int):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, date, time FROM appointments WHERE user_id = ? AND date >= ? ORDER BY date, time",
        (user_id, date.today().isoformat()),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.delete("/api/appointments/{appointment_id}")
def cancel(appointment_id: int, user_id: int):
    conn = get_db()
    result = conn.execute(
        "DELETE FROM appointments WHERE id = ? AND user_id = ?", (appointment_id, user_id)
    )
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(404, "Appointment not found")
    return {"message": "Appointment canceled"}


# ---------- Serve the frontend (keep this last) ----------

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(Path(__file__).parent))
