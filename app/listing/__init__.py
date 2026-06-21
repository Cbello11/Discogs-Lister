from flask import Blueprint

listing_bp = Blueprint("listing", __name__, url_prefix="/listing")

from app.listing import routes  # noqa: E402, F401
