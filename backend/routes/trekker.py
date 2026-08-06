"""Everything a logged-in Trekker can do: browse/book treks, manage their
own bookings, view/edit their profile."""
from flask import Blueprint, request, session, jsonify
from extensions import db
from models import User, Trek, Booking
from routes.access_guard import require_role
from helpers_core import is_valid_phone
from redis_cache import cache_get, cache_set, cache_delete_prefix

trekker_bp = Blueprint("trekker", __name__)


@trekker_bp.route("/dashboard", methods=["GET"])
@require_role("Trekker")
def dashboard():
    open_treks = Trek.query.filter_by(status="Open", archived=False).limit(6).all()
    active_bookings = Booking.query.filter_by(user_id=session["uid"], status="Booked").all()
    return jsonify({
        "treks": [t.to_dict() for t in open_treks],
        "bookings": [b.to_dict() for b in active_bookings],
    })


@trekker_bp.route("/treks", methods=["GET"])
@require_role("Trekker")
def browse_treks():
    q = (request.args.get("q") or "").strip()
    level = request.args.get("level", "all")
    place = request.args.get("place", "all")
    from_date = (request.args.get("date") or "").strip()
    page = request.args.get("page", 1, type=int)

    # The common "no filters applied" listing is the hot path, so it's
    # cached per page for a short window (spec asks for Redis caching here).
    cache_key = f"treks:trekker:{q}:{level}:{place}:{from_date}:{page}"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    treks = Trek.query.filter_by(archived=False)
    if q:
        like = f"%{q}%"
        treks = treks.filter(db.or_(Trek.name.ilike(like), Trek.place.ilike(like)))
    if level != "all":
        treks = treks.filter_by(level=level)
    if place != "all":
        treks = treks.filter_by(place=place)
    if from_date:
        # start_date is stored 'YYYY-MM-DD', so string comparison already
        # sorts the same way real date comparison would.
        treks = treks.filter(Trek.start_date >= from_date)
    treks = treks.order_by(Trek.id.desc())

    known_places = [row[0] for row in db.session.query(Trek.place).distinct().all()]

    per_page = 10
    page = page if page and page > 0 else 1
    total_rows = treks.count()
    page_items = treks.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = -(-total_rows // per_page) if total_rows else 1

    payload = {
        "treks": [t.to_dict() for t in page_items],
        "places": known_places,
        "page": page,
        "total_pages": max(total_pages, 1),
    }
    cache_set(cache_key, payload, ttl_seconds=60)
    return jsonify(payload)


@trekker_bp.route("/treks/<int:trek_id>", methods=["GET"])
@require_role("Trekker")
def trek_detail(trek_id):
    trek = Trek.query.filter_by(id=trek_id, archived=False).first_or_404()
    already_booked = Booking.query.filter_by(
        user_id=session["uid"], trek_id=trek.id, status="Booked"
    ).first() is not None
    return jsonify({"trek": trek.to_dict(), "already_booked": already_booked})


@trekker_bp.route("/treks/<int:trek_id>/book", methods=["POST"])
@require_role("Trekker")
def book_trek(trek_id):
    trek = Trek.query.filter_by(id=trek_id, archived=False).first_or_404()

    if trek.status != "Open":
        return jsonify({"error": "This trek is not open for booking."}), 400
    if trek.seats_left <= 0:
        return jsonify({"error": "No seats left."}), 400
    existing = Booking.query.filter_by(user_id=session["uid"], trek_id=trek.id, status="Booked").first()
    if existing:
        return jsonify({"error": "You already booked this trek."}), 400

    booking = Booking(user_id=session["uid"], trek_id=trek.id)
    trek.seats_left -= 1
    db.session.add(booking)
    db.session.commit()
    cache_delete_prefix("treks:")
    return jsonify(booking.to_dict()), 201


@trekker_bp.route("/bookings", methods=["GET"])
@require_role("Trekker")
def my_bookings():
    # Every booking for this Trekker - active, cancelled and completed all
    # live on the one "My Bookings" page.
    bookings = Booking.query.filter_by(user_id=session["uid"]).order_by(Booking.booked_on.desc()).all()
    return jsonify([b.to_dict() for b in bookings])


@trekker_bp.route("/bookings/<int:bid>/cancel", methods=["POST"])
@require_role("Trekker")
def cancel_booking(bid):
    booking = Booking.query.filter_by(id=bid, user_id=session["uid"]).first_or_404()
    if booking.status == "Booked":
        booking.status = "Cancelled"
        trek = Trek.query.get(booking.trek_id)
        if trek and not trek.archived:
            trek.seats_left += 1
        db.session.commit()
        cache_delete_prefix("treks:")
    return jsonify(booking.to_dict())


@trekker_bp.route("/profile", methods=["GET"])
@require_role("Trekker")
def get_profile():
    return jsonify(User.query.get(session["uid"]).to_dict())


@trekker_bp.route("/profile", methods=["PUT"])
@require_role("Trekker")
def update_profile():
    me = User.query.get(session["uid"])
    data = request.get_json() or {}

    new_phone = (data.get("phone") or me.phone or "").strip()
    if new_phone and not is_valid_phone(new_phone):
        return jsonify({"error": "Phone number must be exactly 10 digits."}), 400

    me.username = (data.get("username") or me.username).strip()
    me.phone = new_phone
    session["username"] = me.username
    db.session.commit()
    return jsonify(me.to_dict())
