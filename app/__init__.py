from flask import Flask, app
from .extensions import db, login_manager, migrate
from .auth.routes import auth_bp
from .main.routes import main_bp
from flask_login import current_user
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Ensure uploads folder exists
    upload_folder = app.config.get("UPLOAD_FOLDER")
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)


    from app import models

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    return app
