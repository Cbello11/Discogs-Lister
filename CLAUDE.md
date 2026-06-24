# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Discogs-Lister is a browser-based Flask app for creating and managing record listings on the Discogs marketplace. It wraps the Discogs API (OAuth 1.0a or personal token) with a GUI for searching releases, drafting listings, uploading images, bulk-submitting, and tracking sales history.

## Running the App

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Discogs credentials
python run.py          # starts at http://127.0.0.1:5000
```

There are no test or lint commands — the project has no test suite or linting config.

## Environment Variables (`.env`)

| Variable | Purpose |
|---|---|
| `DISCOGS_CONSUMER_KEY` / `DISCOGS_CONSUMER_SECRET` | OAuth 1.0a credentials |
| `DISCOGS_PERSONAL_TOKEN` | Simpler alternative to OAuth |
| `FLASK_SECRET_KEY` | Flask session secret |
| `APP_NAME`, `APP_VERSION`, `APP_CONTACT` | Discogs API user-agent metadata |

## Architecture

The app uses Flask blueprints, one per feature area:

- **`app/auth/`** — Login via OAuth flow or personal token; session management
- **`app/search/`** — Search page (mostly client-side via `search.js`)
- **`app/listing/`** — Draft create/edit/autosave (30s intervals), bulk queue submission, image upload
- **`app/history/`** — View/filter past listings, CSV export
- **`app/api/`** — Internal JSON endpoints (`/api/search`, `/api/release`, `/api/price`, `/api/drafts`) that power frontend AJAX

**Discogs integration** lives in `app/discogs/`:
- `client.py` — Thin wrapper around `python3-discogs-client`; handles release search, marketplace stats, listing creation, image upload
- `pricing.py` — Marketplace price caching with 1-hour TTL
- `images.py` — File upload/delete with validation

**Database** (`app/models.py`, SQLite via SQLAlchemy):
- `Draft` — Auto-saved listing drafts
- `ListingRecord` — Published listings (history)
- `PriceCache` — Cached pricing data

**Frontend** is vanilla JS + Bootstrap 5 with Jinja2 templates. Key JS files:
- `search.js` — Release search and pagination
- `listing.js` — Draft form submission
- `bulk.js` — Bulk queue management
- `images.js` — Drag-and-drop photo upload

The app factory is in `app/__init__.py`. Config is in `app/config.py` (SQLite DB at `discogs_lister.db`, uploads at `instance/uploads/`, 16 MB max upload).

## Key Patterns

- Authentication is checked via a `before_request` guard in `app/__init__.py`; routes at `/login`, `/static`, and OAuth endpoints are exempt.
- The listing form autosaves drafts every 30 seconds via `listing.js` before final submission to Discogs.
- Bulk listing works by accumulating items in a queue (client-side), then POSTing the batch to the listing route.
- Database migrations are gitignored; schema changes require manual migration or `db.create_all()`.
