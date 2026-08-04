"""Login/role guard used on almost every route."""
from functools import wraps
from flask import session, jsonify


def require_role(role=None):
    """Route decorator: 401 if not logged in, 403 if blocked or wrong role."""
    def decorator(view_fn):
        @wraps(view_fn)
        def wrapped(*args, **kwargs):
            from models import User

            uid = session.get("uid")
            if uid is None:
                return jsonify({"error": "Not logged in"}), 401

            user = User.query.get(uid)
            if user is None:
                session.clear()
                return jsonify({"error": "Not logged in"}), 401

            if user.blocked:
                session.clear()
                return jsonify({"error": "This account has been blocked."}), 403

            if role and session.get("role") != role:
                return jsonify({"error": "You are not authorized to view that page."}), 403

            return view_fn(*args, **kwargs)
        return wrapped
    return decorator
