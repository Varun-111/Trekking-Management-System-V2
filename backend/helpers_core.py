"""
Small utility functions shared across the route files - phone/password
validation, date parsing, pagination, and the trek clash/duplicate checks
used when Admin creates or edits a trek.
"""
from datetime import datetime
from config import Config


def is_valid_phone(phone):
    phone = (phone or "").strip()
    return phone.isdigit() and len(phone) == 10


def is_valid_password(pwd):
    return bool(pwd) and len(pwd) >= 6


def to_date(text):
    """'YYYY-MM-DD' -> date object, or None if missing/unparsable."""
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def paginate_query(query, page, per_page=None):
    per_page = per_page or Config.PER_PAGE
    page = page if page and page > 0 else 1
    total = query.count()
    rows = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = -(-total // per_page) if total else 1
    return rows, max(total_pages, 1)


def staff_has_overlap(Trek, staff_id, start, end, exclude_trek_id=None):
    """True when `staff_id` is already leading another (non-completed,
    non-archived) trek whose date range clashes with [start, end]."""
    if not staff_id or not start or not end:
        return False

    q = Trek.query.filter_by(staff_id=staff_id, archived=False).filter(Trek.status != "Completed")
    if exclude_trek_id:
        q = q.filter(Trek.id != exclude_trek_id)

    for other in q.all():
        other_start = to_date(other.start_date)
        other_end = to_date(other.end_date)
        if other_start and other_end and start <= other_end and other_start <= end:
            return True
    return False


def is_duplicate_trek(Trek, name, place, start_date_str, exclude_trek_id=None):
    q = Trek.query.filter_by(name=name, place=place, start_date=start_date_str, archived=False)
    if exclude_trek_id:
        q = q.filter(Trek.id != exclude_trek_id)
    return q.first() is not None