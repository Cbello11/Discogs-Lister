import csv
import io
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, Response
from app.ebay import ebay_bp
from app.models import EbayListing
from app.database import db


@ebay_bp.route("/")
def overview():
    status = request.args.get("status")
    query = EbayListing.query
    if status:
        query = query.filter(EbayListing.status == status)
    listings = query.order_by(EbayListing.listed_at.desc()).all()
    return render_template("ebay/overview.html", listings=listings)


@ebay_bp.route("/weekly-review")
def weekly_review():
    today = datetime.utcnow().date()
    # Default window: listings from 7–14 days ago (last week)
    week_offset = int(request.args.get("week", 0))
    end_date = today - timedelta(days=week_offset * 7)
    start_date = end_date - timedelta(days=7)

    listings = (
        EbayListing.query
        .filter(EbayListing.listed_at >= datetime.combine(start_date, datetime.min.time()))
        .filter(EbayListing.listed_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time()))
        .order_by(EbayListing.listed_at.desc())
        .all()
    )

    # Stats
    total = len(listings)
    active = sum(1 for l in listings if l.status == "active")
    sold = sum(1 for l in listings if l.status == "sold")
    ended = sum(1 for l in listings if l.status == "ended")
    total_value = sum(l.price or 0 for l in listings if l.status == "active")
    sold_value = sum(l.price or 0 for l in listings if l.status == "sold")

    return render_template(
        "ebay/weekly_review.html",
        listings=listings,
        start_date=start_date,
        end_date=end_date,
        week_offset=week_offset,
        total=total,
        active=active,
        sold=sold,
        ended=ended,
        total_value=total_value,
        sold_value=sold_value,
    )


@ebay_bp.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        listed_at_str = request.form.get("listed_at")
        listed_at = datetime.strptime(listed_at_str, "%Y-%m-%d") if listed_at_str else datetime.utcnow()

        listing = EbayListing(
            ebay_listing_id=request.form.get("ebay_listing_id") or None,
            title=request.form.get("title", "").strip(),
            artist=request.form.get("artist", "").strip() or None,
            format=request.form.get("format") or None,
            condition=request.form.get("condition") or None,
            price=float(request.form.get("price")) if request.form.get("price") else None,
            currency=request.form.get("currency", "USD"),
            ebay_url=request.form.get("ebay_url", "").strip() or None,
            status=request.form.get("status", "active"),
            notes=request.form.get("notes", "").strip() or None,
            listed_at=listed_at,
        )
        db.session.add(listing)
        db.session.commit()
        flash("eBay listing added.", "success")
        return redirect(url_for("ebay.weekly_review"))

    return render_template("ebay/add.html", listing=None, today=datetime.utcnow().strftime("%Y-%m-%d"))


@ebay_bp.route("/<int:listing_id>/edit", methods=["GET", "POST"])
def edit(listing_id):
    listing = EbayListing.query.get_or_404(listing_id)

    if request.method == "POST":
        listed_at_str = request.form.get("listed_at")
        listing.listed_at = datetime.strptime(listed_at_str, "%Y-%m-%d") if listed_at_str else listing.listed_at
        listing.ebay_listing_id = request.form.get("ebay_listing_id") or None
        listing.title = request.form.get("title", "").strip()
        listing.artist = request.form.get("artist", "").strip() or None
        listing.format = request.form.get("format") or None
        listing.condition = request.form.get("condition") or None
        listing.price = float(request.form.get("price")) if request.form.get("price") else None
        listing.currency = request.form.get("currency", "USD")
        listing.ebay_url = request.form.get("ebay_url", "").strip() or None
        listing.status = request.form.get("status", "active")
        listing.views = int(request.form.get("views")) if request.form.get("views") else None
        listing.watchers = int(request.form.get("watchers")) if request.form.get("watchers") else None
        listing.notes = request.form.get("notes", "").strip() or None
        listing.last_reviewed_at = datetime.utcnow()
        db.session.commit()
        flash("Listing updated.", "success")
        return redirect(request.referrer or url_for("ebay.weekly_review"))

    return render_template(
        "ebay/add.html",
        listing=listing,
        today=listing.listed_at.strftime("%Y-%m-%d") if listing.listed_at else datetime.utcnow().strftime("%Y-%m-%d"),
    )


@ebay_bp.route("/<int:listing_id>/delete", methods=["POST"])
def delete(listing_id):
    listing = EbayListing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    flash("Listing deleted.", "success")
    return redirect(url_for("ebay.overview"))


@ebay_bp.route("/export.csv")
def export_csv():
    listings = EbayListing.query.order_by(EbayListing.listed_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date Listed", "eBay ID", "Title", "Artist", "Format", "Condition", "Price", "Currency", "Status", "Views", "Watchers", "Notes", "eBay URL", "Last Reviewed"])
    for l in listings:
        writer.writerow([
            l.listed_at.strftime("%Y-%m-%d") if l.listed_at else "",
            l.ebay_listing_id or "",
            l.title, l.artist or "", l.format or "", l.condition or "",
            l.price or "", l.currency, l.status,
            l.views if l.views is not None else "",
            l.watchers if l.watchers is not None else "",
            l.notes or "", l.ebay_url or "",
            l.last_reviewed_at.strftime("%Y-%m-%d") if l.last_reviewed_at else "",
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=ebay_listings.csv"},
    )
