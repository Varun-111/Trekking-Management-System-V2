"""Login / register / logout / who-am-i."""
from flask import Blueprint, request, session, jsonify
from extensions import db
from models import User
from helpers_core import is_valid_phone, is_valid_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Only Trekkers can self-register; Trek Staff accounts are created by
    the Admin only - see /api/admin/staff."""
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm = data.get("confirm") or ""
    phone = (data.get("phone") or "").strip()

    if not (name and email and password and phone):
        return jsonify({"error": "Please fill all fields."}), 400
    if not is_valid_phone(phone):
        return jsonify({"error": "Phone number must be exactly 10 digits."}), 400
    if not is_valid_password(password):
        return jsonify({"error": "Password must be at least 6 characters."}), 400
    if password != confirm:
        return jsonify({"error": "Passwords do not match."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    trekker = User(name=name, email=email, role="Trekker", phone=phone, approved=True)
    trekker.set_password(password)
    db.session.add(trekker)
    db.session.commit()

    return jsonify({"message": "Registered! You can log in now."}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role")

    user = User.query.filter_by(email=email, role=role).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Wrong email, password or role."}), 401
    if user.blocked:
        return jsonify({"error": "This account is blocked. Contact admin."}), 403
    if not user.approved:
        return jsonify({"error": "Your account is waiting for admin approval."}), 403

    session["uid"] = user.id
    session["role"] = user.role
    session["name"] = user.name
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out."})


@auth_bp.route("/me", methods=["GET"])
def me():
    uid = session.get("uid")
    if uid is None:
        return jsonify({"user": None})

    user = User.query.get(uid)
    if user is None:
        session.clear()
        return jsonify({"user": None})

    return jsonify({"user": user.to_dict()})
