import sys
import os

# Add root directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app
from backend.extensions import db

def init_database():
    """Create all relational tables and schema structure."""
    app = create_app()
    with app.app_context():
        print("[Database] Creating all tables according to SQLAlchemy metadata models...")
        db.create_all()
        print("[Database] Database schema initialized successfully.")

if __name__ == "__main__":
    init_database()
