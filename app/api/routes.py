from flask import request, jsonify
from app.api import api_bp
from app.discogs import client as dc
from app.discogs.pricing import get_price_suggestions
from app.models import Draft
from app.database import db


@api_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    fmt = request.args.get("format", "All")
    page = int(request.args.get("page", 1))
    if not q:
        return jsonify({"results": [], "total": 0})
    try:
        data = dc.search_releases(q, fmt=fmt, page=page)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/release/<int:release_id>")
def release(release_id):
    try:
        data = dc.get_release(release_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/price/<int:release_id>")
def price(release_id):
    try:
        data = get_price_suggestions(release_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/drafts")
def list_drafts():
    drafts = Draft.query.order_by(Draft.updated_at.desc()).all()
    return jsonify({"drafts": [d.to_dict() for d in drafts]})


@api_bp.route("/draft/<int:draft_id>", methods=["DELETE"])
def delete_draft(draft_id):
    draft = Draft.query.get_or_404(draft_id)
    db.session.delete(draft)
    db.session.commit()
    return jsonify({"ok": True})
