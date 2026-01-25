"""Constants for the Advanced Shelly integration."""

DOMAIN = "advanced_shelly"

# Configuration
CONF_HOST = "host"
CONF_URL = "url"
CONF_NAME = "name"
CONF_BACKUP_PATH = "backup_path"
CONF_BACKUP_INTERVAL = "backup_interval"
CONF_PASSWORD = "password"
SHELLY_USERNAME = "admin"  # Always 'admin' for Shelly devices

# Defaults
DEFAULT_BACKUP_PATH = "/config/shelly_backups"
DEFAULT_BACKUP_INTERVAL = 86400  # 24 hours in seconds
DEFAULT_NAME = "Shelly Device"

# Services
SERVICE_BACKUP_NOW = "backup_now"
SERVICE_RESTORE_SCRIPT = "restore_script"

# Attributes
ATTR_DEVICE_ID = "device_id"
ATTR_SCRIPT_ID = "script_id"
ATTR_BACKUP_PATH = "backup_path"
