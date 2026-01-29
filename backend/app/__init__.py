from flask import Flask, request
import os
from flask_socketio import SocketIO
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
    
    # CORS: manual after_request to avoid flask-cors "function is not iterable" with some configs
    # CORS_ORIGINS: comma-separated list, e.g. https://scraper-frontend.onrender.com,https://scraper-frontend-vbe2.onrender.com
    cors_val = os.getenv('CORS_ORIGINS', '*')
    _cors_origins_list = [o.strip() for o in str(cors_val).split(',') if o and o.strip()] if cors_val and str(cors_val).strip() != '*' else []
    
    def _is_origin_allowed(origin):
        if not origin:
            return False
        if origin in _cors_origins_list:
            return True
        if origin.endswith('.onrender.com'):
            return True
        if '.vercel.app' in origin:
            return True
        if origin.startswith('http://localhost') or origin.startswith('http://127.0.0.1'):
            return True
        return False

    def _add_cors_to_response(response):
        """Add CORS headers - call from both after_request and OPTIONS handler."""
        origin = request.headers.get('Origin')
        if origin and (_is_origin_allowed(origin) or not _cors_origins_list):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        elif not origin:
            response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type'
        return response

    @app.after_request
    def _add_cors_headers(response):
        return _add_cors_to_response(response)
    
    @app.before_request
    def _cors_preflight():
        if request.method == 'OPTIONS':
            from flask import make_response
            resp = make_response('', 204)
            return _add_cors_to_response(resp)

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
    # Socket.IO needs explicit list; use CORS_ORIGINS + allow *.onrender.com for preview URLs
    socketio_origins = _cors_origins_list if _cors_origins_list else '*'
    socketio.init_app(app, cors_allowed_origins=socketio_origins, async_mode='eventlet')
    
    # Register WebSocket event handlers
    register_socketio_events(socketio)

    # JSON error handler for API 500s (helps frontend show real error)
    @app.errorhandler(500)
    def handle_500(e):
        from flask import jsonify
        msg = str(e) if app.debug else 'Internal server error'
        return jsonify({'success': False, 'message': msg}), 500

    return app
