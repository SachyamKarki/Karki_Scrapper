from flask import Flask
import os
from .routes import main

def create_app():
    app = Flask(__name__)
    
    # Load config
    from config import SECRET_KEY
    app.config['SECRET_KEY'] = SECRET_KEY
    
    # Register Blueprint
    app.register_blueprint(main)
    
    return app
