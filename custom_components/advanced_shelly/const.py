"""Constants for the Advanced Shelly integration."""

DOMAIN = "advanced_shelly"

# Configuration
CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"
CONF_BACKUP_PATH = "backup_path"
CONF_BACKUP_INTERVAL = "backup_interval"
CONF_PASSWORD = "password"
SHELLY_USERNAME = "admin"  # Always 'admin' for Shelly devices

# Defaults
DEFAULT_BACKUP_PATH = "/config/shelly_backups"
DEFAULT_BACKUP_INTERVAL = 86400  # 24 hours in seconds
DEFAULT_NAME = "Shelly Device"
DEFAULT_PORT = 80

# RPC rate limiting (recent firmware answers 429 to bursts of RPC calls)
DEFAULT_REQUEST_INTERVAL = 0.5  # minimum seconds between RPC calls
DEFAULT_MAX_RETRIES = 4  # retries after a 429 before giving up
DEFAULT_BACKOFF = 1.0  # first backoff in seconds, doubled on each retry
MAX_BACKOFF = 30.0

# Services
SERVICE_BACKUP_NOW = "backup_now"
SERVICE_RESTORE_SCRIPT = "restore_script"
SERVICE_RESTORE_CONFIG = "restore_config"

# Attributes
ATTR_DEVICE_ID = "device_id"
ATTR_SCRIPT_ID = "script_id"
ATTR_BACKUP_PATH = "backup_path"

# Platforms
PLATFORMS = ["sensor", "binary_sensor"]
