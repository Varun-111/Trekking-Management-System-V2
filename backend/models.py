from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)   # Admin / Trek Staff / Trekker
    phone = db.Column(db.String(20))
    approved = db.Column(db.Boolean, default=True)     # False until Admin approves (Trek Staff only)
    blocked = db.Column(db.Boolean, default=False)      # blacklisted flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "approved": self.approved,
            "blocked": self.blocked,
            "created_at": self.created_at,
        }
    
class StaffProfile(db.Model):
    """Extra profile info for a Trek Staff member (1-to-1 with User)."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    designation = db.Column(db.String(80), default="Trek Guide")
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text)

    user = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        return {
            "designation": self.designation,
            "experience_years": self.experience_years,
            "bio": self.bio,
        }

class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), nullable=False)    # Easy / Moderate / Hard
    days = db.Column(db.Integer, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    seats_left = db.Column(db.Integer, nullable=False)

    # Pending (no staff yet) / Approved (staff assigned) / Open / Closed / Completed
    # Pending -> Approved happens automatically the moment Admin assigns staff.
    # Approved -> Open / Closed / Completed is set directly by the assigned
    # Trek Staff - no admin approval needed for that step.
    status = db.Column(db.String(20), default="Pending")

    staff_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    notes = db.Column(db.Text)
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))

    archived = db.Column(db.Boolean, default=False)   # soft-delete, keeps booking history intact

    staff = db.relationship("User", foreign_keys=[staff_id])

    def booked_count(self):
        return self.total_seats - self.seats_left

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "place": self.place,
            "level": self.level,
            "days": self.days,
            "total_seats": self.total_seats,
            "seats_left": self.seats_left,
            "status": self.status,
            "staff_id": self.staff_id,
            "staff_username": self.staff.username if self.staff else None,
            "notes": self.notes,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "archived": self.archived,
            "booked_count": self.booked_count(),
        }

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    status = db.Column(db.String(20), default="Booked")  # Booked / Cancelled / Completed
    booked_on = db.Column(db.DateTime, default=datetime.utcnow)
    reminder_sent = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship("User", foreign_keys=[user_id])
    trek = db.relationship("Trek", foreign_keys=[trek_id], backref="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_username": self.user.username if self.user else None,
            "user_email": self.user.email if self.user else None,
            "trek_id": self.trek_id,
            "trek_name": self.trek.name if self.trek else None,
            "trek_place": self.trek.place if self.trek else None,
            "trek_start_date": self.trek.start_date if self.trek else None,
            "trek_end_date": self.trek.end_date if self.trek else None,
            "status": self.status,
            "booked_on": self.booked_on.strftime("%Y-%m-%d %H:%M") if self.booked_on else None,
        }


class TrekNudge(db.Model):
    """
    Tracks a one-time 'you haven't booked this upcoming trek yet' reminder
    email so the daily job doesn't re-email the same user about the same
    trek every single day.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "trek_id", name="uq_nudge_user_trek"),)
