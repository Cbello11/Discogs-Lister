import discogs_client
from flask import (
    render_template, request, redirect, url_for,
    session, flash, current_app
)
from app.auth import auth_bp


def _make_oauth_client():
    cfg = current_app.config
    ua = f"{cfg['APP_NAME']}/{cfg['APP_VERSION']} +{cfg['APP_CONTACT']}"
    return discogs_client.Client(
        ua,
        consumer_key=cfg["DISCOGS_CONSUMER_KEY"],
        consumer_secret=cfg["DISCOGS_CONSUMER_SECRET"],
    )


@auth_bp.route("/login")
def login():
    return render_template("auth/login.html")


@auth_bp.route("/oauth/start")
def oauth_start():
    d = _make_oauth_client()
    try:
        token, secret, url = d.get_authorize_url(callback_url=url_for("auth.oauth_callback", _external=True))
        session["oauth_request_token"] = token
        session["oauth_request_secret"] = secret
        return redirect(url)
    except Exception as e:
        flash(f"OAuth error: {e}", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/callback")
def oauth_callback():
    verifier = request.args.get("oauth_verifier")
    token = session.pop("oauth_request_token", None)
    secret = session.pop("oauth_request_secret", None)
    if not verifier or not token:
        flash("OAuth flow failed. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    d = _make_oauth_client()
    d.set_token(token, secret)
    try:
        access_token, access_secret = d.get_access_token(verifier)
        session["discogs_access_token"] = access_token
        session["discogs_access_secret"] = access_secret
        identity = d.identity()
        session["discogs_username"] = identity.username
        session["discogs_avatar"] = getattr(identity, "avatar_url", "")
        flash(f"Connected as {identity.username}!", "success")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Could not complete OAuth: {e}", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/token", methods=["POST"])
def token_login():
    token = request.form.get("personal_token", "").strip()
    if not token:
        flash("Please enter your personal access token.", "warning")
        return redirect(url_for("auth.login"))

    cfg = current_app.config
    ua = f"{cfg['APP_NAME']}/{cfg['APP_VERSION']} +{cfg['APP_CONTACT']}"
    try:
        d = discogs_client.Client(ua, user_token=token)
        identity = d.identity()
        session["discogs_personal_token"] = token
        session["discogs_username"] = identity.username
        session["discogs_avatar"] = getattr(identity, "avatar_url", "")
        flash(f"Connected as {identity.username}!", "success")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Invalid token or connection error: {e}", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
