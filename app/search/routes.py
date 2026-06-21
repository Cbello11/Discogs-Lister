from flask import render_template
from app.search import search_bp


@search_bp.route("/")
def search():
    return render_template("search/search.html")
