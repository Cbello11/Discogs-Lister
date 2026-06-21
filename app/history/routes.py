import csv
import io
from flask import render_template, request, Response
from app.history import history_bp
from app.models import ListingRecord


@history_bp.route("/")
def history():
    query = ListingRecord.query
    fmt = request.args.get("format")
    condition = request.args.get("condition")
    status = request.args.get("status")
    if fmt:
        query = query.filter(ListingRecord.format.ilike(f"%{fmt}%"))
    if condition:
        query = query.filter(ListingRecord.media_condition == condition)
    if status:
        query = query.filter(ListingRecord.status == status)
    records = query.order_by(ListingRecord.listed_at.desc()).all()
    return render_template("history/history.html", records=records)


@history_bp.route("/export.csv")
def export_csv():
    records = ListingRecord.query.order_by(ListingRecord.listed_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Artist", "Title", "Format", "Media Condition", "Sleeve Condition", "Price", "Currency", "Status", "Discogs URL"])
    for r in records:
        writer.writerow([
            r.listed_at.strftime("%Y-%m-%d %H:%M") if r.listed_at else "",
            r.artist, r.release_title, r.format,
            r.media_condition, r.sleeve_condition,
            r.final_price, r.currency, r.status, r.discogs_url or "",
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=discogs_history.csv"},
    )
