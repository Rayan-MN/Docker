# Project 3: Flask and PostgreSQL without Docker Compose

This project runs the Project 2 Flask application and PostgreSQL as separate containers. They communicate over a user-created Docker bridge network; no Docker Compose is used. The Flask image keeps the same multi-stage Dockerfile pattern as Project 2.

## Files

- `Dockerfile` — multi-stage production image for Flask and Gunicorn.
- `app.py` — Flask routes, including `GET /database` for a live PostgreSQL query.
- `db/init.sql` — creates and seeds `app_messages` when PostgreSQL first initializes its data directory.

## Prerequisites

Docker must be installed and running. Run all commands below from this directory:

```bash
cd "3.multi-container-app"
```

## Build and run

1. Create the network. Docker DNS makes container names resolvable only to containers on this network.

```bash
docker network create flask-postgres-net
```

2. Start PostgreSQL. The named volume preserves database data across container replacement. The init script is run only when that volume is empty for the first time.

```bash
docker volume create flask-postgres-data
docker run -d \
  --name postgres \
  --network flask-postgres-net \
  --network-alias postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=appdb \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=change-me \
  -v flask-postgres-data:/var/lib/postgresql/data \
  -v "$(pwd)/db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" \
  postgres:17-alpine
```

3. Wait until PostgreSQL reports that it is ready:

```bash
until docker exec postgres pg_isready -U appuser -d appdb; do sleep 1; done
```

4. Build the Flask image and run it on the same network. `POSTGRES_HOST=postgres` is deliberately the database **container name**, not `localhost`.

```bash
docker build -t flask-postgres-app:1.0 .
docker run -d \
  --name flask-app \
  --network flask-postgres-net \
  -p 8000:8000 \
  -e APP_ENV=production \
  -e POSTGRES_HOST=postgres \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB=appdb \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=change-me \
  flask-postgres-app:1.0
```

For real deployments, supply `POSTGRES_PASSWORD` through a secret manager or an environment file outside version control, rather than using the example value.

## Verify

```bash
docker ps
curl http://localhost:8000/health
curl http://localhost:8000/database
docker network inspect flask-postgres-net
```

Expected `/database` response (the timestamp-independent fields):

```json
{"database":"appdb","message_count":1,"status":"ok","user":"appuser"}
```

You can also inspect the initialized table directly:

```bash
docker exec -it postgres psql -U appuser -d appdb -c "SELECT * FROM app_messages;"
```

## Stop and clean up

```bash
docker rm -f flask-app postgres
docker network rm flask-postgres-net
```

The `flask-postgres-data` volume is intentionally retained. To reset the database and cause `db/init.sql` to run again, remove it after both containers are stopped:

```bash
docker volume rm flask-postgres-data
```
