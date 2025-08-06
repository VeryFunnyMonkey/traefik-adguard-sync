# Traefik-AdGuard Sync

This project syncs hostnames from a Traefik dynamic configuration file to AdGuard Home DNS rewrites. It monitors changes to the Traefik config and updates AdGuard Home so that all configured hosts resolve to your Traefik instance IP.

## Features

- Watches Traefik's dynamic config for changes
- Syncs DNS rewrites in AdGuard Home to match Traefik hosts
- Adds/removes DNS records as needed
- Runs as a Docker container

## Usage

### 1. Configure Environment Variables

Copy [`.env.example`](.env.example) and rename it to `.env`. Fill in the env variables

```env
ADGUARD_URL=http://<adguard-ip>:<port>
ADGUARD_USER=<adguard-username>
ADGUARD_PASSWORD=<adguard-password>
TRAEFIK_IP=<traefik-ip>
```

### 2. Run with Docker Compose

Copy [`example-docker-compose.yml`](example-docker-compose.yml) and rename it to `docker-compose.yml`. Set the volume to the path of your Traefik config folder

```sh
docker compose up -d
```

### 3. How It Works

- The container runs [`sync.py`](sync.py), which:
  - Reads Traefik's dynamic config (`dynamic.yml`)
  - Extracts hostnames from router rules
  - Syncs DNS rewrites in AdGuard Home to point to your Traefik IP
  - Watches for config changes and re-syncs automatically