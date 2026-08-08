"""Celery background jobs: daily trek-reminder emails, the monthly admin
report, and a Trekker's on-demand CSV export."""
import os
import csv
from datetime import datetime, timedelta
from celery_worker import celery
from config import Config
from notify import send_mail

from app import create_app
flask_app = create_app()


@celery.task(name="scheduled_tasks.send_daily_reminders")
def send_daily_reminders():
    """Nudges every Trekker who hasn't booked a seat on an Open trek that
    starts within Config.REMINDER_WINDOW_DAYS. Each (user, trek) pair is
    only ever nudged once, tracked via the TrekNudge table."""
    with flask_app.app_context():
        from extensions import db
        from models import User, Trek, Booking, TrekNudge
        from helpers_core import to_date

        today = datetime.utcnow().date()
        horizon = today + timedelta(days=Config.REMINDER_WINDOW_DAYS)

        upcoming_treks = []
        for trek in Trek.query.filter_by(status="Open", archived=False).all():
            start = to_date(trek.start_date)
            if start and today < start <= horizon:
                upcoming_treks.append(trek)

        active_trekkers = User.query.filter_by(role="Trekker", blocked=False).all()

        sent_count = 0
        for trek in upcoming_treks:
            booked_ids = {b.user_id for b in Booking.query.filter_by(trek_id=trek.id, status="Booked").all()}
            nudged_ids = {n.user_id for n in TrekNudge.query.filter_by(trek_id=trek.id).all()}

            for user in active_trekkers:
                if user.id in booked_ids or user.id in nudged_ids:
                    continue

                subject = f"RidgeLine: seats still open on '{trek.name}' ({trek.start_date})"
                html = f"""
                <html><body style="font-family: Arial, sans-serif; background:#f4f9f5; padding:24px; color:#1c2a20;">
                <div style="max-width:480px; margin:0 auto; background:#ffffff; border:1px solid #dbe8dd; border-radius:14px; overflow:hidden;">
                  <div style="background:#16a34a; padding:16px 22px;">
                    <span style="color:#ffffff; font-size:1.05rem; font-weight:700;">RidgeLine</span>
                  </div>
                  <div style="padding:22px;">
                    <h2 style="margin:0 0 10px; font-size:1.15rem;">{trek.name} departs in {Config.REMINDER_WINDOW_DAYS} days</h2>
                    <p style="margin:0 0 14px;">Hi {user.name}, you haven't booked a seat on this trek yet - grab one before it fills up.</p>
                    <table cellpadding="6" style="width:100%; border-collapse:collapse; font-size:0.92rem;">
                      <tr><td style="color:#64766a;">Location</td><td>{trek.place}</td></tr>
                      <tr><td style="color:#64766a;">Departure</td><td>{trek.start_date}</td></tr>
                      <tr><td style="color:#64766a;">Duration</td><td>{trek.days} day(s)</td></tr>
                      <tr><td style="color:#64766a;">Difficulty</td><td>{trek.level}</td></tr>
                      <tr><td style="color:#64766a;">Seats left</td><td>{trek.seats_left}</td></tr>
                    </table>
                    {f'<p style="margin-top:14px;">{trek.notes}</p>' if trek.notes else ""}
                    <p style="margin-top:18px; color:#64766a; font-size:0.85rem;">Log in to RidgeLine to book your spot.</p>
                  </div>
                </div>
                </body></html>
                """
                delivered = send_mail(user.email, subject, html)
                if delivered:
                    db.session.add(TrekNudge(user_id=user.id, trek_id=trek.id))
                    sent_count += 1

        db.session.commit()
        return f"Sent {sent_count} reminder(s) across {len(upcoming_treks)} trek(s) in the next {Config.REMINDER_WINDOW_DAYS} days"


@celery.task(name="scheduled_tasks.generate_monthly_report")
def generate_monthly_report():
    """Runs on the 1st of the month: builds an HTML activity snapshot and
    emails it to Config.ADMIN_REPORT_EMAIL, plus saves a copy to disk."""
    with flask_app.app_context():
        from extensions import db
        from models import Trek, Booking, User

        os.makedirs(Config.REPORTS_DIR, exist_ok=True)

        treks_conducted = Trek.query.filter_by(status="Completed").count()
        total_members = User.query.filter_by(role="Trekker").count()
        total_bookings = Booking.query.count()

        top_treks = (
            db.session.query(Trek.name, db.func.count(Booking.id).label("cnt"))
            .join(Booking, Booking.trek_id == Trek.id)
            .group_by(Trek.id)
            .order_by(db.desc("cnt"))
            .limit(5)
            .all()
        )
        if top_treks:
            rows_html = "".join(
                f"<tr><td style='padding:6px 12px;'>{i}. {name}</td><td style='padding:6px 12px;'>{count} booking(s)</td></tr>"
                for i, (name, count) in enumerate(top_treks, start=1)
            )
        else:
            rows_html = "<tr><td style='padding:6px 12px;' colspan='2'>Nothing booked yet this period.</td></tr>"

        month_label = datetime.utcnow().strftime("%B %Y")
        html = f"""<html><body style="font-family: Arial, sans-serif; background:#f4f9f5; padding:24px; color:#1c2a20;">
<div style="max-width:500px; margin:0 auto; background:#ffffff; border:1px solid #dbe8dd; border-radius:14px; overflow:hidden;">
  <div style="background:#16a34a; padding:16px 22px;">
    <span style="color:#ffffff; font-size:1.05rem; font-weight:700;">RidgeLine Snapshot - {month_label}</span>
  </div>
  <div style="padding:22px;">
    <p style="color:#64766a; margin-top:0;">A quick roundup of what happened on the platform this month.</p>
    <table cellpadding="8" style="width:100%; border-collapse:collapse; font-size:0.92rem;">
      <tr><td style="color:#64766a;">Expeditions wrapped up</td><td><b>{treks_conducted}</b></td></tr>
      <tr><td style="color:#64766a;">Trekkers on the platform</td><td><b>{total_members}</b></td></tr>
      <tr><td style="color:#64766a;">Total bookings all-time</td><td><b>{total_bookings}</b></td></tr>
    </table>
    <h3 style="margin-top:20px; font-size:1rem;">Crowd Favorites</h3>
    <table cellpadding="6" style="width:100%; border-collapse:collapse; font-size:0.9rem;">
    {rows_html}
    </table>
    <p style="color:#64766a; font-size:0.82rem; margin-top:20px;">Sent automatically on the 1st of every month.</p>
  </div>
</div>
</body></html>"""

        filename = f"monthly_report_{datetime.utcnow().strftime('%Y_%m')}.html"
        with open(os.path.join(Config.REPORTS_DIR, filename), "w") as f:
            f.write(html)

        emailed = send_mail(Config.ADMIN_REPORT_EMAIL, f"RidgeLine Snapshot - {month_label}", html)
        return {"filename": filename, "emailed": emailed}


@celery.task(name="scheduled_tasks.export_trekker_history_csv", bind=True)
def export_trekker_history_csv(self, user_id):
    """Trekker-triggered async job: writes the calling user's full booking
    history (active + past) to a CSV file they can download."""
    with flask_app.app_context():
        from models import User, Booking

        os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
        user = User.query.get(user_id)
        bookings = Booking.query.filter_by(user_id=user_id).all()

        filename = f"trekking_history_user_{user_id}_{self.request.id}.csv"
        filepath = os.path.join(Config.EXPORTS_DIR, filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Trek Name", "Place", "Booking Status", "Booked On",
                              "Trek Start Date", "Trek End Date"])
            for booking in bookings:
                trek = booking.trek
                writer.writerow([
                    user_id,
                    trek.name if trek else "-",
                    trek.place if trek else "-",
                    booking.status,
                    booking.booked_on.strftime("%Y-%m-%d") if booking.booked_on else "-",
                    trek.start_date if trek else "-",
                    trek.end_date if trek else "-",
                ])

        return {"filename": filename, "status": "done", "user": user.email if user else None}
