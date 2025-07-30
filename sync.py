import os
import time
import yaml
import re
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Configuration from Environment Variables ---
ADGUARD_URL = os.getenv("ADGUARD_URL")
ADGUARD_USER = os.getenv("ADGUARD_USER")
ADGUARD_PASSWORD = os.getenv("ADGUARD_PASSWORD")
TRAEFIK_IP = os.getenv("TRAEFIK_IP")
CONFIG_PATH = os.getenv("CONFIG_PATH", "/config")
DYNAMIC_CONFIG_FILE = "dynamic.yml"
FULL_CONFIG_PATH = os.path.join(CONFIG_PATH, DYNAMIC_CONFIG_FILE)

# --- Core Functions ---

def get_traefik_hosts(file_path):
    """Parses the Traefik dynamic config to extract hostnames."""
    hosts = set()
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        if config and 'http' in config and 'routers' in config['http']:
            for _, router in config['http']['routers'].items():
                if 'rule' in router:
                    matches = re.findall(r"Host\(`([^`]+)`\)", router['rule'])
                    if matches:
                        hosts.update(matches)
        return hosts
    except FileNotFoundError:
        print(f"Error: Config file not found at {file_path}. Waiting...")
        return set()
    except Exception as e:
        print(f"Error parsing YAML file: {e}")
        return set()

def sync_to_adguard():
    """Connects to AdGuard Home and syncs DNS rewrites by adding and removing hosts."""
    print("\nStarting full sync to AdGuard Home...")
    desired_hosts = get_traefik_hosts(FULL_CONFIG_PATH)
    
    session = requests.Session()
    # Retry authentication until successful
    while True:
        try:
            session.post(
                f"{ADGUARD_URL}/control/login",
                json={"name": ADGUARD_USER, "password": ADGUARD_PASSWORD},
                timeout=10
            ).raise_for_status()
            break  # Exit loop if successful
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect or authenticate with AdGuard: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    # Get existing rewrites that are managed by this script
    try:
        response = session.get(f"{ADGUARD_URL}/control/rewrite/list")
        response.raise_for_status()
        # Only manage records pointing to the Traefik IP
        managed_hosts = {
            rewrite['domain'] for rewrite in response.json()
            if rewrite.get('answer') == TRAEFIK_IP
        }
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch existing AdGuard rewrites: {e}")
        return

    # Calculate differences
    hosts_to_add = desired_hosts - managed_hosts
    hosts_to_remove = managed_hosts - desired_hosts
    
    # Add new hosts
    if hosts_to_add:
        print(f"Adding {len(hosts_to_add)} new host(s)...")
        for host in hosts_to_add:
            print(f"  -> Adding: {host}")
            session.post(f"{ADGUARD_URL}/control/rewrite/add", json={"domain": host, "answer": TRAEFIK_IP})
    
    # Remove stale hosts
    if hosts_to_remove:
        print(f"Removing {len(hosts_to_remove)} stale host(s)...")
        for host in hosts_to_remove:
            print(f"  -> Removing: {host}")
            session.post(f"{ADGUARD_URL}/control/rewrite/delete", json={"domain": host, "answer": TRAEFIK_IP})

    if not hosts_to_add and not hosts_to_remove:
        print("DNS is already in sync. No changes needed.")
    else:
        print("Sync complete.")


# --- File Monitoring Logic ---

class ConfigChangeHandler(FileSystemEventHandler):
    """Handles file system events for the config file."""
    def on_modified(self, event):
        if not event.is_directory and event.src_path == FULL_CONFIG_PATH:
            print(f"\nDetected change in {DYNAMIC_CONFIG_FILE}. Re-syncing in 3 seconds...")
            time.sleep(3) # Wait a moment for file write to complete
            sync_to_adguard()

if __name__ == "__main__":
    if not all([ADGUARD_URL, ADGUARD_USER, ADGUARD_PASSWORD, TRAEFIK_IP]):
        print("Critical environment variables are missing. Please check your configuration.")
    else:
        print("sync.py started")
        sync_to_adguard() # Initial sync on startup
        event_handler = ConfigChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, path=CONFIG_PATH, recursive=False)
        observer.start()
        print(f"\nWatching for changes in {FULL_CONFIG_PATH}...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
