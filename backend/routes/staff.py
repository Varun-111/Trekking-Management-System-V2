"""Everything a logged-in Trek Staff member can do: manage their assigned
treks, view participants, edit their own profile."""
from flask import Blueprint, request, session, jsonify
from extensions import db
from models import User, StaffProfile, Trek, Booking
from routes.access_guard import require_role
from helpers_core import is_valid_phone
from redis_cache import cache_delete_prefix

staff_bp = Blueprint("staff", __name__)


@staff_bp.route("/dashboard", methods=["GET"])
@require_role("Trek Staff")
def dashboard():
    my_treks = Trek.query.filter_by(staff_id=session["uid"], archived=False).all()
    return jsonify({"treks": [t.to_dict() for t in my_treks]})


@staff_bp.route("/trek/<int:trek_id>", methods=["GET"])
@require_role("Trek Staff")
def trek_detail(trek_id):
    trek = Trek.query.filter_by(id=trek_id, staff_id=session["uid"], archived=False).first_or_404()
    roster = Booking.query.filter_by(trek_id=trek.id).filter(Booking.status != "Cancelled").all()
    my_treks = Trek.query.filter_by(staff_id=session["uid"], archived=False).all()
    return jsonify({
        "trek": trek.to_dict(),
        "bookings": [b.to_dict() for b in roster],
        "my_treks": [t.to_dict() for t in my_treks],
    })


@staff_bp.route("/trek/<int:trek_id>", methods=["PUT"])
@require_role("Trek Staff")
def update_trek(trek_id):
    trek = Trek.query.filter_by(id=trek_id, staff_id=session["uid"], archived=False).first_or_404()
    data = request.get_json() or {}

    if data.get("seats_left") is not None:
        try:
            seats = int(data["seats_left"])
            if 0 <= seats <= trek.total_seats:
                trek.seats_left = seats
        except (TypeError, ValueError):
            pass

    message = "Trek updated."
    new_status = data.get("status")
    if new_status and new_status != trek.status and new_status in ("Open", "Closed", "Completed"):
        trek.status = new_status
        message = f"Trek status updated to {new_status}."
        if new_status == "Completed":
            for booking in trek.bookings:
                if booking.status == "Booked":
                    booking.status = "Completed"

    db.session.commit()
    cache_delete_prefix("treks:")
    return jsonify({"trek": trek.to_dict(), "message": message})


@staff_bp.route("/participants", methods=["GET"])
@require_role("Trek Staff")
def participants():
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)

    roster = Booking.query.join(Trek).filter(Trek.staff_id == session["uid"], Booking.status != "Cancelled")
    if q:
        roster = roster.join(User, Booking.user_id == User.id).filter(User.name.ilike(f"%{q}%"))
    roster = roster.order_by(Booking.booked_on.desc())

    per_page = 10
    page = page if page and page > 0 else 1
    total_rows = roster.count()
    page_items = roster.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = -(-total_rows // per_page) if total_rows else 1

    return jsonify({
        "bookings": [b.to_dict() for b in page_items],
        "page": page,
        "total_pages": max(total_pages, 1),
    })


@staff_bp.route("/profile", methods=["GET"])
@require_role("Trek Staff")
def get_profile():
    me = User.query.get(session["uid"])
    profile = StaffProfile.query.filter_by(user_id=me.id).first()
    if profile is None:
        profile = StaffProfile(user_id=me.id)
        db.session.add(profile)
        db.session.commit()
    return jsonify({"me": me.to_dict(), "profile": profile.to_dict()})


@staff_bp.route("/profile", methods=["PUT"])
@require_role("Trek Staff")
def update_profile():
    me = User.query.get(session["uid"])
    profile = StaffProfile.query.filter_by(user_id=me.id).first()
    if profile is None:
        profile = StaffProfile(user_id=me.id)
        db.session.add(profile)
        db.session.commit()

    data = request.get_json() or {}
    new_phone = (data.get("phone") or me.phone or "").strip()
    if new_phone and not is_valid_phone(new_phone):
        return jsonify({"error": "Phone number must be exactly 10 digits."}), 400

    me.name = (data.get("name") or me.name).strip()
    me.phone = new_phone
    profile.designation = (data.get("designation") or profile.designation or "").strip()
    if data.get("experience_years") is not None:
        try:
            profile.experience_years = int(data["experience_years"])
        except (TypeError, ValueError):
            pass
    profile.bio = data.get("bio", profile.bio)

    session["name"] = me.name
    db.session.commit()
    return jsonify({"me": me.to_dict(), "profile": profile.to_dict()})
