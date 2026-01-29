"""WSGI entry point for gunicorn (Render production)."""
# CRITICAL: eventlet.monkey_patch() MUST run before any other imports
import eventlet
eventlet.monkey_patch()

from app import create_app

app = create_app()
