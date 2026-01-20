import os

class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024