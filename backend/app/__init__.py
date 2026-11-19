import os
import sys
import logging
from flask import Flask, render_template

from backend.config import config_by_name, Config
from backend.extensions import db, migrate, login_manager

logger = logging.getLogger(__name__)


def download_nltk_resources():
    """Download required NLTK tokenizers and corpora safely."""
    try:
        import nltk

        resources = [
            "punkt",
            "punkt_tab",
            "stopwords",
            "wordnet",
            "averaged_perceptron_tagger",
            "averaged_perceptron_tagger_eng",
            "maxent_ne_chunker",
            "maxent_ne_chunker_tab",
            "words",
        ]
        for resource in resources:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                logger.debug("NLTK resource %s skipped or already present: %s", resource, str(e))
    except Exception as e:
        logger.warning("Could not initialize NLTK downloads: %s", str(e))


def create_app(config_name: str = None) -> Flask:
    """Application factory for Flask resume screening tool."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app_config = config_by_name.get(config_name, Config)
    app.config.from_object(app_config)

    # Ensure required directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # User loader callback for Flask-Login
    from backend.app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from backend.app.routes.auth import auth_bp
    from backend.app.routes.dashboard import dashboard_bp
    from backend.app.routes.resumes import resumes_bp
    from backend.app.routes.jobs import jobs_bp
    from backend.app.routes.candidates import candidates_bp
    from backend.app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resumes_bp, url_prefix="/resumes")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(candidates_bp, url_prefix="/candidates")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("layout/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("layout/500.html"), 500

    # Global context processors
    @app.context_processor
    def inject_global_vars():
        from datetime import datetime
        return {
            "current_year": datetime.now().year,
            "app_name": "AntiGravity AI Screener",
        }

    # Download NLTK datasets once in background or during setup
    with app.app_context():
        download_nltk_resources()

    return app
