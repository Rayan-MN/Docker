import os
import socket
from datetime import datetime, timezone

import psycopg
from flask import Flask, jsonify, render_template

app = Flask(__name__)


def database_settings():
    """Return PostgreSQL connection settings supplied by container env vars."""
    return {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": os.getenv("POSTGRES_DB", "appdb"),
        "user": os.getenv("POSTGRES_USER", "appuser"),
        "password": os.getenv("POSTGRES_PASSWORD", "change-me"),
        "connect_timeout": 3,
    }


def database_status():
    """Return non-sensitive details about the PostgreSQL service connection."""
    try:
        with psycopg.connect(**database_settings()) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT current_database(), current_user, "
                    "(SELECT count(*) FROM app_messages)"
                )
                database_name, database_user, message_count = cursor.fetchone()
    except psycopg.Error:
        return {"status": "unavailable"}

    return {
        "status": "connected",
        "database": database_name,
        "user": database_user,
        "message_count": message_count,
    }


@app.get("/")
def home():
    database = database_status()
    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        stage=os.getenv("APP_STAGE", "unknown"),
        served_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        database_host=os.getenv("POSTGRES_HOST", "postgres"),
        database=database,
    )


@app.get("/health")
def health():
    return jsonify(
        status="ok",
        environment=os.getenv("APP_ENV", "development"),
        time=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/database")
def database():
    """Verify the app can resolve and query the PostgreSQL service."""
    details = database_status()
    if details["status"] == "unavailable":
        return jsonify(status="error", database="unavailable"), 503

    return jsonify(
        status="ok",
        database=details["database"],
        user=details["user"],
        message_count=details["message_count"],
    )


if __name__ == "__main__":
    debug_mode = os.getenv("APP_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=8000, debug=debug_mode)
