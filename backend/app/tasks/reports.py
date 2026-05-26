"""Report generation tasks"""
# Re-export from alerts.py for organizational purposes
from app.tasks.alerts import generate_weekly_reports

__all__ = ["generate_weekly_reports"]
