from flask import Flask, request
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
    
    import re
    # CORS configuration
    cors_val = os.getenv('CORS_ORIGINS', '*')
    if cors_val == '*':
        # Use regex to allow all origins while supporting credentials
        _cors_origins_list = [re.compile(r"https?://.*")] 
    else:
        _cors_origins_list = [o.strip() for o in str(cors_val).split(',') if o and o.strip()]
    
    # Nuclear CORS: Always allow Vercel and Localhost for robustness
    # Using compiled regex objects ensures flask-cors treats them as patterns
    _cors_origins_list.append(re.compile(r"https?://.*\.vercel\.app"))
    _cors_origins_list.append(re.compile(r"https?://localhost:\d+"))
    
    CORS(app, resources={r"/*": {
        "origins": _cors_origins_list,
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }})

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
    
    # Initialize SocketIO - threading (stable on Render, no eventlet/gevent)
    # SocketIO expects '*' or a specific list of origins. If we used regex for CORS, use '*' here.
    socketio_origins = _cors_origins_list if _cors_origins_list and _cors_origins_list != [r".*"] else '*'
    socketio.init_app(app, cors_allowed_origins=socketio_origins, async_mode='threading')
    
    # Register WebSocket event handlers
    register_socketio_events(socketio)

    # JSON error handler for API 500s (helps frontend show real error)
    @app.errorhandler(500)
    def handle_500(e):
        from flask import jsonify
        msg = str(e) if app.debug else 'Internal server error'
        return jsonify({'success': False, 'message': msg}), 500

    return app
