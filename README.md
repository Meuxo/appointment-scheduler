# Appointment Scheduling System

SE 480 Team 3 project. A simple web app for a barbershop where customers book appointments online and the owner sets business hours.

**Tech stack:** Python (FastAPI), HTML/CSS, SQLite

## Project structure

```
backend/
  main.py        FastAPI app and all API routes
  database.py    SQLite setup (tables are created automatically)
frontend/
  index.html     Log in / create account
  customer.html  View open times, book, cancel, see upcoming appointments
  owner.html     Business owner sets open days and hours
  style.css      Styling (works on phone and computer)
  app.js         Shared helper functions
```

## How to run

1. Install Python 3.10 or newer.
2. In the project folder, install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Start the app:
   ```
   python backend/main.py
   ```
4. Open http://127.0.0.1:8000 in your browser.

The database file (`backend/app.db`) is created the first time you run it. Delete it any time to start fresh.

API docs are at http://127.0.0.1:8000/docs.

## Trying it out

1. Create an account and check "I'm the business owner", then log in and set some hours.
2. Log out, create a regular customer account, log in, and book a time.

## Requirements covered

| Requirement | Where |
|---|---|
| 1. Registration and login (hashed passwords) | `/api/register`, `/api/login`, `index.html` |
| 2. Business sets hours, customers view open slots | `/api/hours`, `/api/slots`, `owner.html` |
| 3. Book, cancel, and view appointments (no double bookings) | `/api/appointments`, `customer.html` |

Double bookings are blocked by a `UNIQUE(date, time)` rule on the appointments table, so the database rejects a second booking for the same slot.

## Who owns what

| Area | Owner |
|---|---|
| Project setup, database, GitHub | Dominic |
| Registration and login | TJ |
| Business hours and open slots | Nimo |
| Booking and cancellation | Dominic, TJ |
| Responsive UI and testing | Shane |

## Working together

- Pull before you start: `git pull`
- Make a branch for your feature: `git checkout -b login-page`
- Commit and push your branch, then open a pull request on GitHub.
- Don't commit `app.db` (it's already in `.gitignore`).
