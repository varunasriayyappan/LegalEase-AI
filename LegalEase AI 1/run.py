"""Run the whole LegalEase app (FastAPI + Streamlit) from ONE terminal:

    python run.py
"""
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

from config import API_HOST, API_PORT, API_URL, BASE_DIR, STREAMLIT_PORT, ensure_logo


def wait_for_api(timeout: int = 40) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(API_URL + "/", timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def main() -> None:
    ensure_logo()

    print(f"[LegalEase] Starting backend on {API_URL} ...")
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "legalEaseAPI.main:app",
         "--host", API_HOST, "--port", str(API_PORT)],
        cwd=BASE_DIR,
    )

    try:
        if not wait_for_api():
            print("[LegalEase] Backend failed to start. Check errors above.")
            return

        print("[LegalEase] Backend ready. Starting frontend ...")
        url = f"http://localhost:{STREAMLIT_PORT}"
        threading.Timer(3, lambda: webbrowser.open(url)).start()

        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
             "--server.port", str(STREAMLIT_PORT),
             "--server.headless", "true",
             "--browser.gatherUsageStats", "false"],
            cwd=BASE_DIR,
        )
    except KeyboardInterrupt:
        pass
    finally:
        print("\n[LegalEase] Shutting down ...")
        api.terminate()
        try:
            api.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api.kill()


if __name__ == "__main__":
    main()