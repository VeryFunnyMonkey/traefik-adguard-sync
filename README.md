# Traefik-AdGuard Sync

This project syncs hostnames from a Traefik dynamic configuration file to AdGuard Home DNS rewrites. It monitors changes to the Traefik config and updates AdGuard Home so that all configured hosts resolve to your Traefik instance IP.

## Features

- Watches Traefik's dynamic config for changes
- Syncs DNS rewrites in AdGuard Home to match Traefik hosts
- Adds/removes DNS records as needed
- Runs as a Docker container

## Usage

### 1. Clone the repository

```sh
git clone https://github.com/yourusername/traefik-adguard-sync.git
cd traefik-adguard-sync
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory (see [`.env.example`](.env.example) for an exmple):

```env
ADGUARD_URL=http://<adguard-ip>:<port>
ADGUARD_USER=<adguard-username>
ADGUARD_PASSWORD=<adguard-password>
TRAEFIK_IP=<traefik-ip>
```

### 3. Build and Run with Docker Compose

Copy [`example-docker-compose.yml`](example-docker-compose.yml) and rename it to `docker-compose.yml`. Set the volume to the path of your Traefik config folder

```sh
docker compose up --build
```

### 4. How It Works

- The container runs [`sync.py`](sync.py), which:
  - Reads Traefik's dynamic config (`dynamic.yml`)
  - Extracts hostnames from router rules
  - Syncs DNS rewrites in AdGuard Home to point to your Traefik IP
  - Watches for config changes and re-syncs automatically

## File Structure

- [`sync.py`](sync.py): Main sync script
- [`dockerfile`](dockerfile): Docker build instructions
- [`example-docker-compose.yml`](example-docker-compose.yml): Example Docker Compose
- [`requirements.txt`](requirements.txt): Python dependencies
- [`.env.example`](.env.example): Example environment file

## Requirements

- Python 3.11+
- AdGuard Home API access
- Traefik with dynamic config

## License

MIT License

---

**Links:**
- [`sync.py`](sync.py)
- [`dockerfile`](dockerfile)
- [`example-docker-compose.yml`](example-docker-compose.yml)
- [`requirements.txt`](requirements.txt)
- [`.env.example`](.env.example)