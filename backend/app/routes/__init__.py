from backend.app.routes.auth import auth_bp
from backend.app.routes.dashboard import dashboard_bp
from backend.app.routes.resumes import resumes_bp
from backend.app.routes.jobs import jobs_bp
from backend.app.routes.candidates import candidates_bp
from backend.app.routes.reports import reports_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "resumes_bp",
    "jobs_bp",
    "candidates_bp",
    "reports_bp",
]
