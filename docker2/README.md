# Production-style Flask multi-stage build

This folder contains a Flask application designed to show the production value of multi-stage Docker builds.

## Run the optimized image

```bash
docker build -t flask-multistage:latest .
docker run --rm --name flask-multistage -p 8000:8000 flask-multistage:latest
```

Visit [http://localhost:8000](http://localhost:8000), or check the health endpoint:

```bash
curl http://localhost:8000/health
```

## Compare it with a single-stage image

```bash
docker build -f Dockerfile.single-stage -t flask-single-stage:latest .
docker build -t flask-multistage:latest .
docker image ls flask-single-stage flask-multistage
```

The comparison image keeps `build-essential` and build artifacts in production. The multi-stage image creates dependency wheels in `builder`, then starts `runtime` from a clean base and copies only what is needed to serve the app.

| Area | Single stage | Multi-stage runtime |
| --- | --- | --- |
| Compiler/build tools | Included | Discarded |
| Dependency install | Downloads/builds in runtime | Uses builder-produced wheels |
| Container user | Root | Unprivileged `app` user |
| Health check | None | Docker `HEALTHCHECK` |

Docker caches the dependency stage because `requirements.txt` is copied before the application code. Application-only edits therefore reuse the dependency layer.
