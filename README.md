# Trekking-Management-System-V2
IITM MAD-2 Project

Trekking Management System

Flask REST API backend + Vue.js 3 frontend (Vite, `npm run dev`) + SQLite + Redis caching + Celery background jobs.

Trek booking platform for three roles: **Admin** (site admin), **Trek Staff**, **Trekker** (member).

## Roles & Key Behaviour

- **Admin** — pre-seeded (`admin@trail.com` / `admin123`, login role: `Admin`). Creates/edits/removes treks, **adds every Trek Staff account directly** (there is no staff sign-up form - see below), blocks/unblocks trekkers and staff, views all bookings, searches users/staff/treks.
- **Trek Staff** — accounts can **only** be created by the Admin from the admin panel; there is no self-registration path for staff, so every staff account is active the moment it's created. Manages assigned treks: updates seats left and sets trek status directly (`Open` / `Closed` / `Completed`) — no admin approval needed for that step.
- **Trekker (member)** — self-registers (the only self-registration path in the app), browses all treks (filter by difficulty/place/search), books `Open` treks, views/cancels bookings, views trekking history, exports booking history as CSV from **My Bookings**, edits profile.

Login requires matching **email + password + role** — selecting the wrong role tab will not log you in even with correct credentials.

## Trek Status Workflow

A trek moves through a fixed lifecycle:

`Pending` → (Admin assigns Trek Staff) → `Approved` → (Trek Staff sets it) → `Open` / `Closed` / `Completed`

- A trek is created as **Pending** when no staff is assigned.
- The moment Admin assigns a Trek Staff member, it becomes **Approved** automatically.
- From there, the assigned Trek Staff member can set the trek to **Open**, **Closed**, or **Completed** directly — no admin approval required.
- Trekkers can only book a trek while it is **Open**.

## Business Rules

- Difficulty is one of `Easy` / `Moderate` / `Hard`.
- A trek's start date must be in the future when created (or edited, unless it's already `Open`/`Closed`/`Completed`).
- No duplicate treks (same name + place + start date).
- A staff member can't be assigned to two treks with overlapping date ranges, and must be an active Trek Staff account.
- Trek seats can't be reduced below the number already booked.
- Removing a trek is a soft-delete (archived) — existing bookings are kept for history, active ones get cancelled.
- Booking is blocked unless the trek's status is exactly `Open` and it has seats left.
- Duplicate booking of the same trek by the same trekker is blocked.
- Marking a trek `Completed` automatically marks all its active bookings `Completed`.
- Cancelling a booking restores a seat (unless the trek has been archived).
- Registration/profile/staff-creation forms enforce: phone number exactly 10 digits, password at least 6 characters, and trek start dates that aren't in the past.

## Project Structure
```
ridgeline/
  backend/
    app.py                # Flask app factory, blueprint registration, Admin seeding
    config.py             # SQLite/Redis/Celery/SMTP config
    extensions.py         # SQLAlchemy instance
    models.py             # User, StaffProfile, Trek, Booking, TrekNudge
    utils.py               # validation, pagination, date-overlap, duplicate-trek checks
    cache.py                # Redis cache helpers (safe no-op if Redis is down)
    celery_worker.py         # Celery instance + beat schedule
    jobs.py                    # Celery jobs: daily reminders, monthly report, CSV export
    mail_service.py              # SMTP helper (with connection timeout)
    test_email.py                  # standalone script to verify SMTP works
    routes/                         # auth, admin, staff, member, export blueprints + guards.py
    requirements.txt
  frontend/
    index.html
    vite.config.js          # dev-server proxy: /api -> Flask on :5000
    src/
      main.js, api.js, store.js, router.js, style.css
      components/ (Navbar.vue, Pagination.vue)
      views/ (Login, Register, NotFound, admin/*, staff/*, member/*)
```

## Running Locally

You need **4-5 terminals**:

```bash
# Terminal 1: Redis
redis-server (requires wsl)

# Terminal 2: Flask backend
cd backend
pip install -r requirements.txt
python test_email.py your-test-address@example.com   # optional: verify SMTP works first
python app.py
# -> API on http://127.0.0.1:5000

# Terminal 3: Frontend (Vite dev server)
cd frontend
npm install
npm run dev
# -> open http://localhost:5173  (proxies /api/* to Flask automatically)

# Terminal 4: Celery worker (handles CSV export)
cd backend
celery -A celery_worker.celery worker --loglevel=info --pool=solo

# Terminal 5 (optional, for reminders/reports): Celery beat
cd backend
celery -A celery_worker.celery beat --loglevel=info
```

**Note (Windows):** the Celery `--pool=solo` flag is required — the default "prefork" pool crashes on Windows (`billiard`/`WinError 6`).

## Building for Production

```bash
cd frontend
npm run build
```
This outputs static files to `frontend/dist/`. Serve them with any static file host (or point Flask at that folder) — the dev-time Vite proxy is only needed for `npm run dev`.

## SMTP / Email

Credentials are pre-filled in `backend/config.py` (can be overridden via `SMTP_HOST`/`SMTP_USER`/`SMTP_PASSWORD`/etc. environment variables). If SMTP isn't reachable, sends are logged to `backend/logs/email_fallback_log.txt` instead of failing silently, and the Celery worker prints a warning banner on startup if credentials are missing.

## Redis Caching

The Trekker "browse treks" listing (`GET /api/member/treks`) is cached per filter combination for 60 seconds, and invalidated automatically whenever a trek is created, edited, deleted, booked, or cancelled.

## Celery Jobs

1. **Daily reminders** (`jobs.send_daily_reminders`, runs 8:00 AM daily) — emails every Trekker about `Open` treks starting within the next `REMINDER_WINDOW_DAYS` (default **7**) days that they haven't booked yet, nudging them to grab a seat. Each (user, trek) pair is only emailed once. The worker log prints a full breakdown of every trek considered and why it was included/skipped, and whether each individual email succeeded or failed — so a "0 sent" result is always diagnosable from the log instead of being a silent mystery. To test immediately:
   ```bash
   cd backend
   python -c "import jobs; print(jobs.send_daily_reminders.run())"
   ```
   Watch the `[reminders]` lines in the output — they'll tell you exactly which trek(s) were in the date window, how many unbooked trekkers there were, and why any were skipped.
2. **Monthly report** (`jobs.generate_monthly_report`, runs 1st of month, 6:00 AM) — emails an HTML activity summary ("RidgeLine Snapshot") to the Admin's report address, and saves a copy to `backend/reports/`.
3. **CSV export** (`jobs.export_trekker_history_csv`, triggered from the Trekker's **My Bookings** page) — exports that user's full booking history to `backend/exports/`. Clicking "Export as CSV" queues the job, polls its status, then automatically downloads the finished file via a hidden `<a download>` link — no new tab, no manual download step.

## Database

Created programmatically via SQLAlchemy (`db.create_all()`), no manual DB Browser usage. The Admin account is seeded automatically on first run.

