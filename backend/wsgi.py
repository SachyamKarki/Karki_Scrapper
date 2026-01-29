"""WSGI entry point for gunicorn (Render production)."""
from app import create_app

app = create_app()
