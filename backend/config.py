
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # ---- core Flask / DB ----
    SECRET_KEY = os.environ.get("SECRET_KEY", "my_secret_key")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'trekking.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PER_PAGE = 10  # rows per page for any long table

    # ---- redis / celery ----
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", f"redis://{REDIS_HOST}:{REDIS_PORT}/2")

    # ---- pre-seeded Admin login ----
    ADMIN_LOGIN_EMAIL = os.environ.get("ADMIN_LOGIN_EMAIL", "23f1000065@ds.study.iitm.ac.in")
    ADMIN_LOGIN_PASSWORD = os.environ.get("ADMIN_LOGIN_PASSWORD", "admin@123")

    # ---- outgoing email ----
    ADMIN_REPORT_EMAIL = os.environ.get("ADMIN_REPORT_EMAIL", "23f1000065@ds.study.iitm.ac.in")  # where the monthly report goes
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "varun2004111k@gmail.com")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "gdcjdnzdllncryno")
    SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USER)

    REMINDER_WINDOW_DAYS = int(os.environ.get("REMINDER_WINDOW_DAYS", 7))

    # ---- file output folders ----
    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
