import time
import json
from datetime import datetime
from flask import (
    render_template, request, redirect, url_for,
    flash, jsonify, current_app, session
)
from app.listing import listing_bp
from app.database import db
from app.models import Draft, ListingRecord
from app.discogs import client as dc
from app.discogs.pricing import get_price_suggestions
from app.discogs.images import save_upload, delete_upload


@listing_bp.route("/new")
def new():
    release_id = request.args.get("release_id")
    if not release_id:
        flash("No release selected.", "warning")
        return redirect(url_for("search.search"))
    try:
        release = dc.get_release(release_id)
    except Exception as e:
        flash(f"Could not load release: {e}", "danger")
        return redirect(url_for("search.search"))

    draft = Draft(
        release_id=release["id"],
        release_title=release["title"],
        artist=", ".join(release["artists"]),
        format=release["formats"][0].get("name", "") if release["formats"] else "",
    )
    db.session.add(draft)
    db.session.commit()

    pricing = {}
    try:
        pricing = get_price_suggestions(release_id)
    except Exception:
        pass

    return render_template("listing/form.html", release=release, draft=draft, pricing=pricing)


@listing_bp.route("/draft/<int:draft_id>")
def edit_draft(draft_id):
    draft = Draft.query.get_or_404(draft_id)
    try:
        release = dc.get_release(draft.release_id)
    except Exception as e:
        flash(f"Could not load release: {e}", "danger")
        return redirect(url_for("listing.drafts"))
    pricing = {}
    try:
        pricing = get_price_suggestions(draft.release_id)
    except Exception:
        pass
    return render_template("listing/form.html", release=release, draft=draft, pricing=pricing)


@listing_bp.route("/draft/<int:draft_id>/save", methods=["POST"])
def save_draft(draft_id):
    draft = Draft.query.get_or_404(draft_id)
    data = request.get_json() or request.form

    draft.media_condition = data.get("media_condition", draft.media_condition)
    draft.sleeve_condition = data.get("sleeve_condition", draft.sleeve_condition)
    draft.price = float(data.get("price") or 0) or draft.price
    draft.currency = data.get("currency", draft.currency)
    draft.comments = data.get("comments", draft.comments)
    draft.location = data.get("location", draft.location)
    draft.quantity = int(data.get("quantity") or 1)
    draft.allow_offers = bool(data.get("allow_offers"))
    draft.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True, "updated_at": draft.updated_at.isoformat()})


@listing_bp.route("/drafts")
def drafts():
    all_drafts = Draft.query.order_by(Draft.updated_at.desc()).all()
    return render_template("listing/drafts.html", drafts=all_drafts)


@listing_bp.route("/draft/<int:draft_id>/delete", methods=["POST"])
def delete_draft(draft_id):
    draft = Draft.query.get_or_404(draft_id)
    for path in draft.image_paths:
        delete_upload(path)
    db.session.delete(draft)
    db.session.commit()
    flash("Draft deleted.", "info")
    return redirect(url_for("listing.drafts"))


@listing_bp.route("/submit/<int:draft_id>", methods=["POST"])
def submit(draft_id):
    draft = Draft.query.get_or_404(draft_id)

    # Update draft with final form values
    draft.media_condition = request.form.get("media_condition")
    draft.sleeve_condition = request.form.get("sleeve_condition")
    draft.price = float(request.form.get("price") or 0)
    draft.currency = request.form.get("currency", "USD")
    draft.comments = request.form.get("comments", "")
    draft.location = request.form.get("location", "")
    draft.quantity = int(request.form.get("quantity") or 1)
    draft.allow_offers = "allow_offers" in request.form
    db.session.commit()

    if not draft.media_condition or not draft.price:
        flash("Please set a condition and price before submitting.", "warning")
        return redirect(url_for("listing.edit_draft", draft_id=draft_id))

    payload = {
        "release_id": draft.release_id,
        "condition": draft.media_condition,
        "sleeve_condition": draft.sleeve_condition or "No Cover",
        "price": draft.price,
        "currency": draft.currency,
        "status": "For Sale",
        "comments": draft.comments or "",
        "allow_offers": draft.allow_offers,
        "location": draft.location or "",
        "weight": "auto",
        "format_quantity": draft.quantity,
    }

    try:
        result = dc.create_listing(payload)
        listing_id = result.get("listing_id")
        listing_url = result.get("resource_url", "").replace("api.", "www.").replace("/marketplace/listings/", "/sell/item/")

        record = ListingRecord(
            draft_id=draft.id,
            discogs_listing_id=listing_id,
            release_id=draft.release_id,
            release_title=draft.release_title,
            artist=draft.artist,
            format=draft.format,
            media_condition=draft.media_condition,
            sleeve_condition=draft.sleeve_condition,
            final_price=draft.price,
            currency=draft.currency,
            discogs_url=listing_url,
        )
        db.session.add(record)
        db.session.delete(draft)
        db.session.commit()

        flash(f"Listed successfully! Listing #{listing_id}", "success")
        return redirect(url_for("listing.success", record_id=record.id))
    except Exception as e:
        flash(f"Error creating listing: {e}", "danger")
        return redirect(url_for("listing.edit_draft", draft_id=draft_id))


@listing_bp.route("/success/<int:record_id>")
def success(record_id):
    record = ListingRecord.query.get_or_404(record_id)
    return render_template("listing/success.html", record=record)


@listing_bp.route("/bulk")
def bulk():
    all_drafts = Draft.query.order_by(Draft.updated_at.desc()).all()
    return render_template("listing/bulk.html", drafts=all_drafts)


@listing_bp.route("/bulk/submit", methods=["POST"])
def bulk_submit():
    draft_ids = request.json.get("draft_ids", [])
    results = []
    for draft_id in draft_ids:
        draft = Draft.query.get(draft_id)
        if not draft:
            results.append({"draft_id": draft_id, "ok": False, "error": "Draft not found"})
            continue
        if not draft.media_condition or not draft.price:
            results.append({"draft_id": draft_id, "ok": False, "error": "Missing condition or price"})
            continue
        payload = {
            "release_id": draft.release_id,
            "condition": draft.media_condition,
            "sleeve_condition": draft.sleeve_condition or "No Cover",
            "price": draft.price,
            "currency": draft.currency or "USD",
            "status": "For Sale",
            "comments": draft.comments or "",
            "allow_offers": draft.allow_offers or False,
            "location": draft.location or "",
            "weight": "auto",
            "format_quantity": draft.quantity or 1,
        }
        try:
            result = dc.create_listing(payload)
            listing_id = result.get("listing_id")
            listing_url = result.get("resource_url", "")
            record = ListingRecord(
                draft_id=draft.id,
                discogs_listing_id=listing_id,
                release_id=draft.release_id,
                release_title=draft.release_title,
                artist=draft.artist,
                format=draft.format,
                media_condition=draft.media_condition,
                sleeve_condition=draft.sleeve_condition,
                final_price=draft.price,
                currency=draft.currency,
                discogs_url=listing_url,
            )
            db.session.add(record)
            db.session.delete(draft)
            db.session.commit()
            results.append({"draft_id": draft_id, "ok": True, "listing_id": listing_id, "title": draft.release_title})
        except Exception as e:
            results.append({"draft_id": draft_id, "ok": False, "error": str(e), "title": draft.release_title})
        time.sleep(1)  # respect Discogs rate limits

    return jsonify({"results": results})


@listing_bp.route("/image/upload/<int:draft_id>", methods=["POST"])
def upload_image(draft_id):
    draft = Draft.query.get_or_404(draft_id)
    if "image" not in request.files:
        return jsonify({"ok": False, "error": "No file"}), 400
    file = request.files["image"]
    if not file.filename:
        return jsonify({"ok": False, "error": "Empty filename"}), 400
    try:
        path = save_upload(file)
        paths = draft.image_paths
        if len(paths) >= 3:
            return jsonify({"ok": False, "error": "Maximum 3 images allowed"}), 400
        paths.append(path)
        draft.image_paths = paths
        db.session.commit()
        return jsonify({"ok": True, "path": path, "index": len(paths) - 1})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@listing_bp.route("/image/delete/<int:draft_id>/<int:index>", methods=["POST"])
def delete_image(draft_id, index):
    draft = Draft.query.get_or_404(draft_id)
    paths = draft.image_paths
    if 0 <= index < len(paths):
        delete_upload(paths[index])
        paths.pop(index)
        draft.image_paths = paths
        db.session.commit()
    return jsonify({"ok": True})
