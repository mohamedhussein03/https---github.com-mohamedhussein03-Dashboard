import os

class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
