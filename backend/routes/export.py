"""Async CSV export of a Trekker's own booking history, backed by a Celery
task (see scheduled_tasks.py) so the request doesn't block on file I/O."""
from flask import Blueprint, session, jsonify, send_from_directory
from routes.access_guard import require_role
from models import User
from config import Config

export_bp = Blueprint("export", __name__)


@export_bp.route("/history/csv", methods=["POST"])
@require_role("Trekker")
def trigger_csv_export():
    from scheduled_tasks import export_trekker_history_csv
    try:
        job = export_trekker_history_csv.delay(session["uid"])
    except Exception as exc:
        return jsonify({"error": f"Could not queue export job. Is Redis/Celery running? ({exc})"}), 503
    return jsonify({"task_id": job.id})


@export_bp.route("/history/csv/status/<task_id>", methods=["GET"])
@require_role("Trekker")
def export_status(task_id):
    from scheduled_tasks import export_trekker_history_csv
    result = export_trekker_history_csv.AsyncResult(task_id)

    if result.state == "SUCCESS":
        payload = result.result or {}
        requester = User.query.get(session["uid"])
        # confirm this export actually belongs to the caller before revealing the filename
        if requester is None or payload.get("user") != requester.email:
            return jsonify({"error": "Forbidden"}), 403
        return jsonify({"state": result.state, "filename": payload.get("filename")})

    if result.state == "FAILURE":
        return jsonify({"state": result.state, "error": str(result.result)})

    return jsonify({"state": result.state})


@export_bp.route("/history/csv/download/<path:filename>", methods=["GET"])
@require_role("Trekker")
def export_download(filename):
    expected_prefix = f"trekking_history_user_{session['uid']}_"
    if not filename.startswith(expected_prefix):
        return jsonify({"error": "Forbidden"}), 403
    return send_from_directory(Config.EXPORTS_DIR, filename, as_attachment=True)
