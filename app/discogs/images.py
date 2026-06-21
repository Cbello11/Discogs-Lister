import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    """Save an uploaded file to the uploads folder and return its path."""
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(upload_dir, filename)
    file.save(path)
    return path


def delete_upload(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
