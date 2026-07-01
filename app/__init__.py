import os
from flask import Flask, session, redirect, url_for, render_template
from app.config import Config
from app.database import db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    from app.auth import auth_bp
    from app.search import search_bp
    from app.listing import listing_bp
    from app.history import history_bp
    from app.api import api_bp
    from app.ebay import ebay_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(listing_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(ebay_bp)

    # Auth guard — skip for auth routes and static
    PUBLIC_ENDPOINTS = {"auth.login", "auth.oauth_start", "auth.oauth_callback", "auth.token_login", "static"}

    @app.before_request
    def require_auth():
        from flask import request
        if request.endpoint in PUBLIC_ENDPOINTS:
            return
        if not session.get("discogs_username"):
            return redirect(url_for("auth.login"))

    @app.route("/")
    def index():
        from datetime import datetime, timedelta
        from app.models import Draft, ListingRecord, EbayListing
        draft_count = Draft.query.count()
        listing_count = ListingRecord.query.count()
        recent = ListingRecord.query.order_by(ListingRecord.listed_at.desc()).limit(5).all()
        ebay_active = EbayListing.query.filter_by(status="active").count()
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        ebay_needs_review = EbayListing.query.filter(
            EbayListing.status == "active",
            EbayListing.listed_at <= one_week_ago,
            db.or_(EbayListing.last_reviewed_at == None, EbayListing.last_reviewed_at <= one_week_ago),
        ).count()
        return render_template(
            "index.html",
            draft_count=draft_count,
            listing_count=listing_count,
            recent=recent,
            ebay_active=ebay_active,
            ebay_needs_review=ebay_needs_review,
        )

    with app.app_context():
        db.create_all()

    return app
