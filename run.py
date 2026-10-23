"""One-command launcher:  python run.py
Trains the model if needed, starts the server and opens the browser."""
import os
import sys
import threading
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

PORT = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    try:
        import uvicorn
        import sklearn, pandas, fastapi  # noqa: F401
    except ImportError:
        sys.exit("Missing packages. Run:  pip install -r requirements.txt")

    if not os.path.exists(os.path.join(ROOT, "models", "model.joblib")):  # trained on YOUR machine
        print("Training model for the first time...")
        from src.train import main as train
        train()

    threading.Thread(target=lambda: (time.sleep(1.5), webbrowser.open(f"http://127.0.0.1:{PORT}")), daemon=True).start()
    print(f"\n  NutriPlan running at http://127.0.0.1:{PORT}   (Ctrl+C to stop)\n")
    uvicorn.run("api.main:app", host="127.0.0.1", port=PORT)
