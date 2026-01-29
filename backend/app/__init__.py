from flask import Flask
import os
from flask_socketio import SocketIO
from flask_cors import CORS
from .routes import main

# Initialize SocketIO (will be attached to app in create_app)
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Load config
    from config import SECRET_KEY
    app.config['SECRET_KEY'] = SECRET_KEY
    # Cross-origin cookies when CORS_ORIGINS is set (frontend on different domain)
    if os.getenv('CORS_ORIGINS') and os.getenv('CORS_ORIGINS') != '*':
        app.config['SESSION_COOKIE_SAMESITE'] = 'None'
        app.config['SESSION_COOKIE_SECURE'] = True
    
    # CORS for cross-origin (frontend on Vercel, backend elsewhere)
    cors_val = os.getenv('CORS_ORIGINS', '*')
    origins = [o.strip() for o in cors_val.split(',')] if cors_val != '*' else '*'
    CORS(app, origins=origins, supports_credentials=True)

    # Initialize Flask-Login
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    
    # Register Blueprints (with prefixes for clean API)
    from .routes import main
    from .auth import auth
    from .admin import admin
    from .messages import messages, register_socketio_events
    
    app.register_blueprint(main, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(messages, url_prefix='/messages')
    
    # Initialize SocketIO - eventlet for WebSocket support on Render
    cors_val = os.getenv('CORS_ORIGINS', '*')
    cors_origins = [o.strip() for o in cors_val.split(',')] if cors_val != '*' else '*'
    socketio.init_app(app, cors_allowed_origins=cors_origins, async_mode='eventlet')
    
    # Register WebSocket event handlers
    register_socketio_events(socketio)
    
    return app
