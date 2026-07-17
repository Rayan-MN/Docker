import os
import socket
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)


def backend_status():
    """Call the internal backend service through Docker's network DNS."""
    host = os.getenv("BACKEND_HOST", "network-echo")
    port = os.getenv("BACKEND_PORT", "5678")
    url = f"http://{host}:{port}/"

    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
    except requests.RequestException:
        return {"status": "unavailable", "service": host}

    return {
        "status": "connected",
        "service": host,
        "response": response.text.strip(),
    }


@app.get("/")
def home():
    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        stage=os.getenv("APP_STAGE", "unknown"),
        served_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        backend=backend_status(),
    )


@app.get("/health")
def health():
    return jsonify(
        status="ok",
        environment=os.getenv("APP_ENV", "development"),
        time=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/backend")
def backend():
    """Return the result of the app-to-service network call."""
    details = backend_status()
    if details["status"] == "unavailable":
        return jsonify(status="error", service=details["service"]), 503

    return jsonify(status="ok", service=details["service"], response=details["response"])


if __name__ == "__main__":
    debug_mode = os.getenv("APP_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=8000, debug=debug_mode)
