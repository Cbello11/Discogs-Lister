from flask import Blueprint

ebay_bp = Blueprint("ebay", __name__, url_prefix="/ebay")

from app.ebay import routes  # noqa: E402, F401
