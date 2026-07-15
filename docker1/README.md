# Local Python Web App

Run the app with Docker:

```bash
docker build -t local-python-web-app .
docker run --rm -p 8000:8000 local-python-web-app
```

Open [http://localhost:8000](http://localhost:8000). The health check is available at [http://localhost:8000/health](http://localhost:8000/health).

For local development without Docker:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```
