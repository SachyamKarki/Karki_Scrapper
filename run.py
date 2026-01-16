from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False, port=5555, host='0.0.0.0', threaded=True)
