import discogs_client
from flask import session, current_app


def get_user_agent():
    cfg = current_app.config
    return f"{cfg['APP_NAME']}/{cfg['APP_VERSION']} +{cfg['APP_CONTACT']}"


def get_client():
    """Return an authenticated Discogs client or raise RuntimeError."""
    cfg = current_app.config
    ua = get_user_agent()

    # Personal token path (simpler)
    token = session.get("discogs_personal_token") or cfg.get("DISCOGS_PERSONAL_TOKEN")
    if token:
        d = discogs_client.Client(ua, user_token=token)
        return d

    # OAuth path
    access_token = session.get("discogs_access_token")
    access_secret = session.get("discogs_access_secret")
    consumer_key = cfg.get("DISCOGS_CONSUMER_KEY")
    consumer_secret = cfg.get("DISCOGS_CONSUMER_SECRET")

    if access_token and access_secret and consumer_key and consumer_secret:
        d = discogs_client.Client(
            ua,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
        )
        d.set_token(access_token, access_secret)
        return d

    raise RuntimeError("Not authenticated")


def is_authenticated():
    try:
        get_client()
        return True
    except RuntimeError:
        return False


def get_identity():
    d = get_client()
    return d.identity()


def search_releases(query, fmt=None, page=1, per_page=25):
    d = get_client()
    kwargs = {"type": "release", "page": page, "per_page": per_page}
    if fmt and fmt != "All":
        kwargs["format"] = fmt

    results = d.search(query, **kwargs)
    items = []
    for r in results.page(page):
        try:
            artist = r.artists[0].name if r.artists else "Unknown"
        except Exception:
            artist = "Unknown"
        try:
            fmt_str = ", ".join([f.get("name", "") for f in r.formats]) if r.formats else ""
        except Exception:
            fmt_str = ""
        items.append({
            "id": r.id,
            "title": r.title,
            "artist": artist,
            "year": getattr(r, "year", ""),
            "format": fmt_str,
            "thumb": getattr(r, "thumb", ""),
            "country": getattr(r, "country", ""),
            "label": r.labels[0].name if r.labels else "",
        })
    return {"results": items, "total": results.count, "page": page, "per_page": per_page}


def get_release(release_id):
    d = get_client()
    r = d.release(int(release_id))
    try:
        artists = [a.name for a in r.artists]
    except Exception:
        artists = []
    try:
        labels = [{"name": l.name, "catno": r.data.get("labels", [{}])[0].get("catno", "")} for l in r.labels]
    except Exception:
        labels = []
    try:
        tracklist = [{"position": t.get("position", ""), "title": t.get("title", ""), "duration": t.get("duration", "")} for t in r.tracklist]
    except Exception:
        tracklist = []
    try:
        formats = r.formats
    except Exception:
        formats = []
    try:
        images = [i.get("uri", "") for i in r.images[:3]] if r.images else []
    except Exception:
        images = []
    try:
        thumb = r.images[0].get("uri150", "") if r.images else ""
    except Exception:
        thumb = ""

    return {
        "id": r.id,
        "title": r.title,
        "artists": artists,
        "year": getattr(r, "year", ""),
        "labels": labels,
        "formats": formats,
        "country": getattr(r, "country", ""),
        "notes": getattr(r, "notes", ""),
        "tracklist": tracklist,
        "images": images,
        "thumb": thumb,
        "genres": getattr(r, "genres", []),
        "styles": getattr(r, "styles", []),
    }


def create_listing(payload):
    """POST a new listing to the Discogs marketplace."""
    d = get_client()
    listing = d.listing(None)
    # Use the raw API since discogs_client doesn't have a create_listing helper
    response = d._fetcher.fetch(
        d, "POST", d._base_url + "/marketplace/listings",
        data=payload,
        content_type="application/json",
    )
    return response[0]  # returns parsed JSON


def upload_image(listing_id, image_path):
    """Upload an image and associate it with a listing."""
    d = get_client()
    with open(image_path, "rb") as f:
        response = d._fetcher.fetch(
            d, "POST", d._base_url + f"/marketplace/listings/{listing_id}/images",
            data={"image": f},
            content_type="multipart/form-data",
        )
    return response[0]
