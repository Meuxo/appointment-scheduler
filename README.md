# Appointment Scheduling System

SE 480 Team 3 project. A simple web app for one barbershop where customers can book appointments online.

**Tech stack:** Python (FastAPI), HTML/CSS, SQLite

## Project structure

```
backend/
  main.py        FastAPI app and API routes
  database.py    SQLite setup (tables are created automatically)
frontend/
  index.html     Log in / create account
  home.html      Page you see after logging in (empty for now)
  style.css      Styling
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

## What's done

- Create an account with an email and password
- Log in and log out

## To do

| Feature | Owner |
|---|---|
| Registration and login (polish) | TJ |
| Business hours and open time slots | Nimo |
| Booking and canceling appointments (no double bookings) | Dominic, TJ |
| Responsive UI and testing | Shane |

## Working together

- Pull before you start: `git pull`
- Make a branch for your feature: `git checkout -b booking-page`
- Commit and push your branch, then open a pull request on GitHub.
- Don't commit `app.db` (it's already in `.gitignore`).
