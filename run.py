import os
import threading
import webbrowser
from app import create_app

app = create_app()

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Discogs Lister is starting...")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    # Open browser after a short delay so Flask is ready
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        threading.Timer(1.5, open_browser).start()
    app.run(debug=True, port=5000)
