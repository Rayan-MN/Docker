from datetime import datetime, timezone

from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok", time=datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
