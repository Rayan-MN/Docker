# Project 4: Manual Docker networking

This project is a networking lab without Docker Compose. It runs a Flask application and an internal HTTP echo service manually, using two user-defined bridge networks:

```text
host browser
    |
published port 8000
    |
stage4-frontend
    |
stage4-flask
    |
stage4-backend
    |
stage4-echo (no published ports)
```

The Flask container is attached to both networks. The echo container is attached only to `stage4-backend`, so Flask calls it internally at `http://network-echo:5678/` using Docker's embedded DNS.

## Default bridge versus user-defined bridge

Containers on Docker's default `bridge` network have network connectivity, but Docker does **not** provide automatic container-name DNS resolution there. This is why this name lookup fails:

```bash
docker run -d --name default-web nginx:alpine
docker run --rm alpine:3.20 wget -qO- http://default-web
# wget: bad address 'default-web'
docker rm -f default-web
```

On a user-defined bridge, Docker provides an embedded DNS server. Containers can reach each other by container name or network alias. The rest of this project uses this model.

## Build and run

Run these commands from this directory.

```bash
docker network create stage4-frontend
docker network create stage4-backend

docker run -d \
  --name stage4-echo \
  --network stage4-backend \
  --network-alias network-echo \
  hashicorp/http-echo:1.0.0 \
  -listen=:5678 \
  -text="backend service reached over Docker DNS"

docker build -t manual-networking-app:1.0 .
docker run -d \
  --name stage4-flask \
  --network stage4-frontend \
  -p 8000:8000 \
  -e APP_ENV=production \
  -e APP_STAGE=networking-lab \
  -e BACKEND_HOST=network-echo \
  -e BACKEND_PORT=5678 \
  manual-networking-app:1.0

docker network connect stage4-backend stage4-flask
```

Open <http://localhost:8000>. The page displays the Flask container information and the live result of its call to `network-echo`.

If port 8000 is already in use, publish a different host port, for example `-p 8001:8000`, and open <http://localhost:8001> instead. The backend service still uses port `5678` internally and needs no `-p` option.

## Inspect the networks

```bash
docker network ls
docker network inspect stage4-frontend
docker network inspect stage4-backend
docker inspect stage4-flask --format '{{.NetworkSettings.Networks}}'
docker exec stage4-flask cat /etc/resolv.conf
curl http://localhost:8000/backend
```

`docker network inspect` shows the IPAM subnet and the connected containers. The `/etc/resolv.conf` output shows Docker's embedded DNS server, typically `127.0.0.11`, on a user-defined network.

Example output from the `stage4-backend` inspection in this lab (container IDs omitted):

```text
Subnet: 172.21.0.0/16
Connected containers:
  stage4-echo  172.21.0.2/16
  stage4-flask 172.21.0.3/16
```

The actual subnet and IP addresses can differ on another machine. The important result is that `stage4-echo` and `stage4-flask` share `stage4-backend`, while only `stage4-flask` also belongs to `stage4-frontend`.

## Published ports versus internal ports

`-p 8000:8000` publishes the Flask application's port to the **host**. It is what lets a browser use `localhost:8000`.

It is unrelated to container-to-container communication. Flask reaches the echo container through the backend network using `network-echo:5678`; no host port is published for the echo service. Keeping it unpublished means the host cannot directly reach it.

## Why manual networking matters, and why Compose exists

This manual approach makes the network model visible: create networks, attach containers, choose aliases, and publish only the ports that need host access. Docker Compose automates this setup by creating a project network and DNS names from service names. Compose is usually preferable for repeatable multi-container applications; this project intentionally uses raw Docker commands to make those mechanics explicit.

## Stop and clean up

```bash
docker rm -f stage4-flask stage4-echo
docker network rm stage4-frontend stage4-backend
```
