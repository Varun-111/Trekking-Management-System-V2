"""Admin-only endpoints: dashboard stats, trek CRUD, staff management,
trekker moderation, booking overview."""
from datetime import date, timedelta
from flask import Blueprint, request, session, jsonify
from extensions import db
from models import User, StaffProfile, Trek, Booking
from routes.access_guard import require_role
from helpers_core import to_date, paginate_query, staff_has_overlap, is_duplicate_trek, is_valid_phone, is_valid_password
from redis_cache import cache_delete_prefix

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard", methods=["GET"])
@require_role("Admin")
def dashboard():
    counts = {
        "treks": Trek.query.filter_by(archived=False).count(),
        "members": User.query.filter_by(role="Trekker").count(),
        "staff": User.query.filter_by(role="Trek Staff").count(),
        "active_bookings": Booking.query.filter_by(status="Booked").count(),
        "cancelled_bookings": Booking.query.filter_by(status="Cancelled").count(),
        "completed_bookings": Booking.query.filter_by(status="Completed").count(),
        "total_bookings": Booking.query.count(),
    }
    recent = Booking.query.order_by(Booking.booked_on.desc()).limit(5).all()
    pending_treks = Trek.query.filter_by(status="Pending", archived=False).all()

    return jsonify({
        "counts": counts,
        "latest": [b.to_dict() for b in recent],
        "pending_treks": [t.to_dict() for t in pending_treks],
    })


@admin_bp.route("/treks", methods=["GET"])
@require_role("Admin")
def list_treks():
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)

    treks = Trek.query.filter_by(archived=False)
    if q:
        like = f"%{q}%"
        treks = treks.filter(db.or_(Trek.name.ilike(like), Trek.place.ilike(like)))
    treks = treks.order_by(Trek.id.desc())

    page_items, total_pages = paginate_query(treks, page)
    return jsonify({"treks": [t.to_dict() for t in page_items], "page": page, "total_pages": total_pages})


@admin_bp.route("/treks", methods=["POST"])
@require_role("Admin")
def add_trek():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    place = (data.get("place") or "").strip()
    level = data.get("level")
    days = int(data.get("days") or 1)
    seats = int(data.get("seats") or 0)
    notes = (data.get("notes") or "").strip()
    start_date = to_date(data.get("start_date"))

    if not (name and place and level and start_date and seats):
        return jsonify({"error": "Please fill all required fields."}), 400
    if start_date <= date.today():
        return jsonify({"error": "Trek start date must be after today."}), 400

    end_date = start_date + timedelta(days=max(days - 1, 0))

    if is_duplicate_trek(Trek, name, place, start_date.isoformat()):
        return jsonify({"error": "A trek with the same name, place and start date already exists."}), 400

    staff_id = data.get("staff_id")
    if staff_id:
        staff_id = int(staff_id)
        staff_user = User.query.filter_by(id=staff_id, role="Trek Staff", blocked=False).first()
        if not staff_user:
            return jsonify({"error": "Selected staff member is not a valid, active Trek Staff account."}), 400
        if staff_has_overlap(Trek, staff_id, start_date, end_date):
            return jsonify({"error": "This staff member is already leading another trek in overlapping dates."}), 400
    else:
        staff_id = None

    trek = Trek(
        name=name, place=place, level=level, days=days,
        total_seats=seats, seats_left=seats,
        status="Approved" if staff_id else "Pending",
        staff_id=staff_id, notes=notes,
        start_date=start_date.isoformat(), end_date=end_date.isoformat(),
    )
    db.session.add(trek)
    db.session.commit()
    cache_delete_prefix("treks:")
    return jsonify(trek.to_dict()), 201


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@require_role("Admin")
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json() or {}

    name = (data.get("name") or trek.name).strip()
    place = (data.get("place") or trek.place).strip()
    level = data.get("level", trek.level)
    days = int(data["days"]) if data.get("days") not in (None, "") else trek.days
    notes = data.get("notes", trek.notes)
    start_date = to_date(data.get("start_date")) or to_date(trek.start_date)

    if start_date <= date.today() and trek.status not in ("Open", "Closed", "Completed"):
        return jsonify({"error": "Trek start date must be after today."}), 400

    end_date = start_date + timedelta(days=max(days - 1, 0))

    already_booked = trek.booked_count()
    total_seats = int(data["seats"]) if data.get("seats") not in (None, "") else trek.total_seats
    if total_seats < already_booked:
        return jsonify({"error": f"Cannot set seats below {already_booked} - that many are already booked."}), 400

    if is_duplicate_trek(Trek, name, place, start_date.isoformat(), exclude_trek_id=trek.id):
        return jsonify({"error": "Another trek with the same name, place and start date already exists."}), 400

    staff_id = data.get("staff_id")
    if staff_id:
        staff_id = int(staff_id)
        staff_user = User.query.filter_by(id=staff_id, role="Trek Staff", blocked=False).first()
        if not staff_user:
            return jsonify({"error": "Selected staff member is not a valid, active Trek Staff account."}), 400
        if staff_has_overlap(Trek, staff_id, start_date, end_date, exclude_trek_id=trek.id):
            return jsonify({"error": "This staff member is already leading another trek in overlapping dates."}), 400
    else:
        staff_id = None

    trek.name = name
    trek.place = place
    trek.level = level
    trek.days = days
    trek.staff_id = staff_id
    trek.notes = notes
    trek.start_date = start_date.isoformat()
    trek.end_date = end_date.isoformat()
    trek.total_seats = total_seats
    trek.seats_left = total_seats - already_booked

    # Status is auto-derived from staff assignment - Admin never sets
    # Open/Closed/Completed directly, that belongs to the assigned staff.
    if not staff_id:
        trek.status = "Pending"
    elif trek.status == "Pending":
        trek.status = "Approved"

    db.session.commit()
    cache_delete_prefix("treks:")
    return jsonify(trek.to_dict())


@admin_bp.route("/treks/<int:trek_id>", methods=["DELETE"])
@require_role("Admin")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    trek.archived = True
    # cancel active bookings but keep the rows so booking history survives
    for booking in trek.bookings:
        if booking.status == "Booked":
            booking.status = "Cancelled"
    db.session.commit()
    cache_delete_prefix("treks:")
    return jsonify({"message": f'Trek "{trek.name}" removed. Past booking records are kept for history.'})


@admin_bp.route("/staff", methods=["GET"])
@require_role("Admin")
def list_staff():
    q = (request.args.get("q") or "").strip()

    active_q = User.query.filter_by(role="Trek Staff", blocked=False)
    blocked_q = User.query.filter_by(role="Trek Staff", blocked=True)
    if q:
        like = f"%{q}%"
        active_q = active_q.filter(db.or_(User.username.ilike(like), User.email.ilike(like)))
        blocked_q = blocked_q.filter(db.or_(User.username.ilike(like), User.email.ilike(like)))

    return jsonify({
        "active": [u.to_dict() for u in active_q.all()],
        "blocked": [u.to_dict() for u in blocked_q.all()],
    })


@admin_bp.route("/staff", methods=["POST"])
@require_role("Admin")
def add_staff():
    """Trek Staff accounts only get created here by the Admin, so every one
    is auto-approved the moment it's created - there's no sign-up flow."""
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    pwd = data.get("password") or ""

    if not (username and email and pwd and phone):
        return jsonify({"error": "Please fill all fields."}), 400
    if not is_valid_phone(phone):
        return jsonify({"error": "Phone number must be exactly 10 digits."}), 400
    if not is_valid_password(pwd):
        return jsonify({"error": "Password must be at least 6 characters."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    staff = User(username=username, email=email, phone=phone, role="Trek Staff", approved=True, blocked=False)
    staff.set_password(pwd)
    db.session.add(staff)
    db.session.commit()

    db.session.add(StaffProfile(user_id=staff.id))
    db.session.commit()
    return jsonify(staff.to_dict()), 201


@admin_bp.route("/staff/<int:uid>", methods=["DELETE"])
@require_role("Admin")
def remove_staff(uid):
    person = User.query.filter_by(id=uid, role="Trek Staff").first_or_404()

    # unassign from any treks first so nothing is left pointing at a ghost staff_id
    for trek in Trek.query.filter_by(staff_id=person.id).all():
        trek.staff_id = None

    StaffProfile.query.filter_by(user_id=person.id).delete()
    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Staff member removed."})


@admin_bp.route("/users", methods=["GET"])
@require_role("Admin")
def list_users():
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)

    trekkers = User.query.filter_by(role="Trekker")
    if q:
        trekkers = trekkers.filter(User.username.ilike(f"%{q}%"))
    trekkers = trekkers.order_by(User.id.desc())

    page_items, total_pages = paginate_query(trekkers, page)
    return jsonify({"users": [u.to_dict() for u in page_items], "page": page, "total_pages": total_pages})


@admin_bp.route("/block/<int:uid>", methods=["POST"])
@require_role("Admin")
def block_user(uid):
    person = User.query.get_or_404(uid)
    if person.role == "Admin":
        return jsonify({"error": "Cannot block the Admin."}), 400
    person.blocked = True
    db.session.commit()
    return jsonify(person.to_dict())


@admin_bp.route("/unblock/<int:uid>", methods=["POST"])
@require_role("Admin")
def unblock_user(uid):
    person = User.query.get_or_404(uid)
    person.blocked = False
    db.session.commit()
    return jsonify(person.to_dict())


@admin_bp.route("/bookings", methods=["GET"])
@require_role("Admin")
def list_bookings():
    page = request.args.get("page", 1, type=int)
    all_bookings = Booking.query.order_by(Booking.booked_on.desc())
    page_items, total_pages = paginate_query(all_bookings, page)
    return jsonify({"bookings": [b.to_dict() for b in page_items], "page": page, "total_pages": total_pages})
