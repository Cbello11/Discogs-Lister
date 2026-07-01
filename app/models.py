import json
from datetime import datetime
from app.database import db


class Draft(db.Model):
    __tablename__ = "drafts"

    id = db.Column(db.Integer, primary_key=True)
    release_id = db.Column(db.Integer, nullable=False)
    release_title = db.Column(db.String(500))
    artist = db.Column(db.String(500))
    format = db.Column(db.String(100))
    media_condition = db.Column(db.String(10))
    sleeve_condition = db.Column(db.String(10))
    price = db.Column(db.Float)
    currency = db.Column(db.String(5), default="USD")
    comments = db.Column(db.Text)
    location = db.Column(db.String(200))
    quantity = db.Column(db.Integer, default=1)
    allow_offers = db.Column(db.Boolean, default=False)
    _image_paths = db.Column("image_paths", db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def image_paths(self):
        return json.loads(self._image_paths or "[]")

    @image_paths.setter
    def image_paths(self, value):
        self._image_paths = json.dumps(value)

    def to_dict(self):
        return {
            "id": self.id,
            "release_id": self.release_id,
            "release_title": self.release_title,
            "artist": self.artist,
            "format": self.format,
            "media_condition": self.media_condition,
            "sleeve_condition": self.sleeve_condition,
            "price": self.price,
            "currency": self.currency,
            "comments": self.comments,
            "location": self.location,
            "quantity": self.quantity,
            "allow_offers": self.allow_offers,
            "image_paths": self.image_paths,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ListingRecord(db.Model):
    __tablename__ = "listing_records"

    id = db.Column(db.Integer, primary_key=True)
    draft_id = db.Column(db.Integer, db.ForeignKey("drafts.id"), nullable=True)
    discogs_listing_id = db.Column(db.Integer)
    release_id = db.Column(db.Integer)
    release_title = db.Column(db.String(500))
    artist = db.Column(db.String(500))
    format = db.Column(db.String(100))
    media_condition = db.Column(db.String(10))
    sleeve_condition = db.Column(db.String(10))
    final_price = db.Column(db.Float)
    currency = db.Column(db.String(5))
    listed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="active")
    discogs_url = db.Column(db.String(500))

    def to_dict(self):
        return {
            "id": self.id,
            "discogs_listing_id": self.discogs_listing_id,
            "release_id": self.release_id,
            "release_title": self.release_title,
            "artist": self.artist,
            "format": self.format,
            "media_condition": self.media_condition,
            "sleeve_condition": self.sleeve_condition,
            "final_price": self.final_price,
            "currency": self.currency,
            "listed_at": self.listed_at.isoformat() if self.listed_at else None,
            "status": self.status,
            "discogs_url": self.discogs_url,
        }


class EbayListing(db.Model):
    __tablename__ = "ebay_listings"

    id = db.Column(db.Integer, primary_key=True)
    ebay_listing_id = db.Column(db.String(50))
    title = db.Column(db.String(500), nullable=False)
    artist = db.Column(db.String(500))
    format = db.Column(db.String(100))
    condition = db.Column(db.String(50))
    price = db.Column(db.Float)
    currency = db.Column(db.String(5), default="USD")
    ebay_url = db.Column(db.String(1000))
    status = db.Column(db.String(20), default="active")  # active, sold, ended
    views = db.Column(db.Integer)
    watchers = db.Column(db.Integer)
    notes = db.Column(db.Text)
    listed_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ebay_listing_id": self.ebay_listing_id,
            "title": self.title,
            "artist": self.artist,
            "format": self.format,
            "condition": self.condition,
            "price": self.price,
            "currency": self.currency,
            "ebay_url": self.ebay_url,
            "status": self.status,
            "views": self.views,
            "watchers": self.watchers,
            "notes": self.notes,
            "listed_at": self.listed_at.isoformat() if self.listed_at else None,
            "last_reviewed_at": self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
        }


class PriceCache(db.Model):
    __tablename__ = "price_cache"

    id = db.Column(db.Integer, primary_key=True)
    release_id = db.Column(db.Integer, unique=True, nullable=False)
    median_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    num_for_sale = db.Column(db.Integer)
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
