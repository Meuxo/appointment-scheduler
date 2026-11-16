import hashlib
import re
import sqlite3
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import get_db, init_db

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = FastAPI(title="Appointment Scheduling System")
init_db()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class AccountBody(BaseModel):
    email: str
    password: str


@app.post("/api/register")
def register(body: AccountBody):
    email = body.email.strip().lower()
    if not EMAIL_PATTERN.match(email):
        raise HTTPException(400, "Please enter a valid email")
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, hash_password(body.password)),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(400, "That email already has an account")
    finally:
        conn.close()
    return {"message": "Account created"}


@app.post("/api/login")
def login(body: AccountBody):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (body.email.strip().lower(),)
    ).fetchone()
    conn.close()
    if not user or user["password_hash"] != hash_password(body.password):
        raise HTTPException(401, "Wrong email or password")
    return {"id": user["id"], "email": user["email"]}


# TODO: business hours and open time slots
# TODO: booking and canceling appointments


# Serve the frontend (keep this last)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(Path(__file__).parent))
