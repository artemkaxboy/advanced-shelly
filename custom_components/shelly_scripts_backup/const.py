"""Constants for the Shelly Scripts Backup integration."""

DOMAIN = "shelly_scripts_backup"

# Configuration
CONF_HOST = "host"
CONF_NAME = "name"
CONF_BACKUP_PATH = "backup_path"
CONF_BACKUP_INTERVAL = "backup_interval"

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
ATTR_SCRIPT_NAME = "script_name"
ATTR_BACKUP_PATH = "backup_path"

# API endpoints
SHELLY_SCRIPT_LIST = "/rpc/Script.List"
SHELLY_SCRIPT_GETCODE = "/rpc/Script.GetCode"
SHELLY_SCRIPT_PUTCODE = "/rpc/Script.PutCode"
SHELLY_DEVICE_INFO = "/rpc/Shelly.GetDeviceInfo"
