"""Flask application factory."""
from flask import Flask
from extensions import db
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config["SECRET_KEY"]

    db.init_app(app)

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.staff import staff_bp
    from routes.trekker import trekker_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(staff_bp, url_prefix="/api/staff")
    app.register_blueprint(trekker_bp, url_prefix="/api/trekker")

    with app.app_context():
        db.create_all()

        from models import User
        # The one Admin account is created programmatically on first boot -
        # there is no admin sign-up route anywhere in the app.
        admin_exists = User.query.filter_by(role="Admin").first() is not None
        if not admin_exists:
            admin = User(name="Admin", email=Config.ADMIN_LOGIN_EMAIL, role="Admin", approved=True)
            admin.set_password(Config.ADMIN_LOGIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()

    @app.route("/api/health")
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
