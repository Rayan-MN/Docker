import os
import socket
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.get("/")
def home():
    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        stage=os.getenv("APP_STAGE", "unknown"),
        served_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )


@app.get("/health")
def health():
    return jsonify(
        status="ok",
        environment=os.getenv("APP_ENV", "development"),
        time=datetime.now(timezone.utc).isoformat(),
    )


if __name__ == "__main__":
    debug_mode = os.getenv("APP_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=8000, debug=debug_mode)
