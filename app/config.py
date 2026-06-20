import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = "sqlite:///discogs_lister.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DISCOGS_CONSUMER_KEY = os.environ.get("DISCOGS_CONSUMER_KEY", "")
    DISCOGS_CONSUMER_SECRET = os.environ.get("DISCOGS_CONSUMER_SECRET", "")
    DISCOGS_PERSONAL_TOKEN = os.environ.get("DISCOGS_PERSONAL_TOKEN", "")

    APP_NAME = os.environ.get("APP_NAME", "DiscogsLister")
    APP_VERSION = os.environ.get("APP_VERSION", "1.0")
    APP_CONTACT = os.environ.get("APP_CONTACT", "")

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
