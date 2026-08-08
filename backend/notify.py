"""
Outgoing email. When SMTP isn't configured (or a send fails), the message
gets appended to a local log file instead of failing loudly, so the rest
of the app (reminders, reports, CSV export) keeps working in dev.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config


def send_mail(to_email, subject, html_body):
    """Returns True once the email is actually handed off to the SMTP
    server, False otherwise (unconfigured or send error)."""
    if not (Config.SMTP_HOST and Config.SMTP_USER and Config.SMTP_PASSWORD):
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        with open(os.path.join(Config.LOGS_DIR, "email_fallback_log.txt"), "a") as f:
            f.write(f"[SMTP NOT CONFIGURED] to={to_email} subject={subject!r}\n\n")
        print(f"[notify] SMTP not configured - skipped sending to {to_email}")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = Config.SMTP_FROM
    message["To"] = to_email
    message.attach(MIMEText(html_body, "html"))

    try:
        # Explicit timeout - an unreachable mail server would otherwise
        # hang the whole Celery worker.
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.sendmail(Config.SMTP_FROM, [to_email], message.as_string())
        print(f"[notify] sent to {to_email} ('{subject}')")
        return True
    except Exception as exc:
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        with open(os.path.join(Config.LOGS_DIR, "email_fallback_log.txt"), "a") as f:
            f.write(f"[SEND FAILED] to={to_email} subject={subject!r} error={exc}\n\n")
        print(f"[notify] FAILED to send to {to_email}: {exc}")
        return False
