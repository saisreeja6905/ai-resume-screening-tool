import os
import sys
from dotenv import load_dotenv

# Set base directories
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

# Ensure PROJECT_ROOT and BACKEND_DIR are in sys.path
for path in [PROJECT_ROOT, BACKEND_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Load .env file from PROJECT_ROOT or BACKEND_DIR
env_file_project = os.path.join(PROJECT_ROOT, ".env")
env_file_backend = os.path.join(BACKEND_DIR, ".env")
if os.path.exists(env_file_project):
    load_dotenv(env_file_project)
elif os.path.exists(env_file_backend):
    load_dotenv(env_file_backend)


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "resume-screener-secret-key-2026-production-ready")

    # Database configuration
    database_url = os.getenv("DATABASE_URL", "sqlite:///resume_screener.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # If it's a relative SQLite path, resolve it relative to BACKEND_DIR
    if database_url.startswith("sqlite:///") and not database_url.startswith("sqlite:////"):
        rel_path = database_url.replace("sqlite:///", "")
        if not os.path.isabs(rel_path):
            database_url = f"sqlite:///{os.path.join(BACKEND_DIR, rel_path)}"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(PROJECT_ROOT, "uploads"))
    if not os.path.isabs(UPLOAD_FOLDER):
        UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    ALLOWED_EXTENSIONS = {"pdf"}

    # NLTK configuration
    NLTK_DATA = os.getenv("NLTK_DATA", None)

    # Application settings
    ITEMS_PER_PAGE = 15
    MATCH_MIN_SCORE_HIGHLIGHT = 70.0


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
