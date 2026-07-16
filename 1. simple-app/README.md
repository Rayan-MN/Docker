# Dockerize a simple Flask app

`simple-app` is the starting point of this Docker portfolio: a small Flask web app packaged in a single container image.

It demonstrates the essential workflow:

- define an application image with a `Dockerfile`
- install Python dependencies in the image
- expose the web-service port
- run the app with Gunicorn

## Build and run

From this directory:

```bash
docker build -t flask-simple:latest .
docker run --rm -p 8000:8000 flask-simple:latest
```

Open [http://localhost:8000](http://localhost:8000). The app also provides a machine-readable health endpoint at [http://localhost:8000/health](http://localhost:8000/health).

## Portfolio progression

This is intentionally a straightforward single-stage Docker build. See `../2. multistage-build-optimization` for the same application evolved into a production-minded multi-stage build with a smaller runtime surface, a non-root user, and Docker health checking.

## Run without Docker

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```
