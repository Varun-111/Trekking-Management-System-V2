import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ridgeline-dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'trekking.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PER_PAGE = 10 

    # ---- pre-seeded Admin login ----
    ADMIN_LOGIN_EMAIL = os.environ.get("ADMIN_LOGIN_EMAIL", "23f1000065@ds.study.iitm.ac.in")
    ADMIN_LOGIN_PASSWORD = os.environ.get("ADMIN_LOGIN_PASSWORD", "admin@123")

    