from app import create_app, socketio
import os

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', '5555'))
    host = os.getenv('HOST', '0.0.0.0')
    socketio.run(app, debug=debug_mode, port=port, host=host, allow_unsafe_werkzeug=debug_mode)
