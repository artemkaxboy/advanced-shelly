"""The Advanced Shelly integration."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_URL,
    CONF_PASSWORD,
    CONF_BACKUP_PATH,
    CONF_BACKUP_INTERVAL,
    DEFAULT_BACKUP_PATH,
    DEFAULT_BACKUP_INTERVAL,
    SERVICE_BACKUP_NOW,
    SERVICE_RESTORE_SCRIPT,
    SERVICE_RESTORE_CONFIG,
    ATTR_DEVICE_ID,
    ATTR_SCRIPT_ID,
    ATTR_BACKUP_PATH,
    PLATFORMS,
)
from .shelly_client import ShellyClient

_LOGGER = logging.getLogger(__name__)

SIGNAL_UPDATE_SHELLY = "shelly_backup_update_{}"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Shelly Scripts Backup from a config entry."""
    url = entry.data[CONF_URL]
    password = entry.data.get(CONF_PASSWORD)
    backup_path = entry.data.get(CONF_BACKUP_PATH, DEFAULT_BACKUP_PATH)
    backup_interval = entry.data.get(CONF_BACKUP_INTERVAL, DEFAULT_BACKUP_INTERVAL)

    # Create backup directory if it doesn't exist
    Path(backup_path).mkdir(parents=True, exist_ok=True)

    # Initialize the coordinator
    coordinator = ShellyBackupCoordinator(hass, url, password, backup_path)

    # Test connection
    try:
        await coordinator.update_device_status()
    except Exception as err:
        _LOGGER.error(f"Failed to connect to Shelly device: {err}")
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Schedule periodic backups
    async def periodic_backup(now):
        """Perform periodic backup."""
        await coordinator.backup_scripts()

    cancel_interval = async_track_time_interval(
        hass, periodic_backup, timedelta(seconds=backup_interval)
    )
    hass.data[DOMAIN][f"{entry.entry_id}_cancel"] = cancel_interval

    # Perform initial backup
    await coordinator.backup_scripts()

    # Register services
    await async_setup_services(hass)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Cancel the periodic backup
    cancel_interval = hass.data[DOMAIN].pop(f"{entry.entry_id}_cancel", None)
    if cancel_interval:
        cancel_interval()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Shelly Scripts Backup."""

    async def handle_backup_now(call: ServiceCall) -> None:
        """Handle manual backup service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)

        if device_id:
            # Backup specific device
            for entry_id, coordinator in hass.data[DOMAIN].items():
                if isinstance(coordinator, ShellyBackupCoordinator):
                    if coordinator.device_id == device_id:
                        await coordinator.backup_scripts()
                        return
            _LOGGER.error("Device with ID %s not found", device_id)
        else:
            # Backup all devices
            for entry_id, coordinator in hass.data[DOMAIN].items():
                if isinstance(coordinator, ShellyBackupCoordinator):
                    await coordinator.backup_scripts()

    async def handle_restore_script(call: ServiceCall) -> None:
        """Handle script restoration service call."""
        device_id = call.data[ATTR_DEVICE_ID]
        script_id = call.data[ATTR_SCRIPT_ID]
        backup_path = call.data.get(ATTR_BACKUP_PATH)

        for entry_id, coordinator in hass.data[DOMAIN].items():
            if isinstance(coordinator, ShellyBackupCoordinator):
                if coordinator.device_id == device_id:
                    await coordinator.restore_script(script_id, backup_path)
                    return

        _LOGGER.error(f"Device with ID {device_id} not found")

    async def handle_restore_config(call: ServiceCall) -> None:
        """Handle configuration restoration service call."""
        device_id = call.data[ATTR_DEVICE_ID]
        backup_path = call.data.get(ATTR_BACKUP_PATH)

        for entry_id, coordinator in hass.data[DOMAIN].items():
            if isinstance(coordinator, ShellyBackupCoordinator):
                if coordinator.device_id == device_id:
                    await coordinator.restore_config(backup_path)
                    return

        _LOGGER.error(f"Device with ID {device_id} not found")

    # Register services only once
    if not hass.services.has_service(DOMAIN, SERVICE_BACKUP_NOW):
        hass.services.async_register(
            DOMAIN,
            SERVICE_BACKUP_NOW,
            handle_backup_now,
            schema=vol.Schema({
                vol.Optional(ATTR_DEVICE_ID): str,
            }),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_RESTORE_SCRIPT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RESTORE_SCRIPT,
            handle_restore_script,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): str,
                vol.Required(ATTR_SCRIPT_ID): vol.Coerce(int),
                vol.Optional(ATTR_BACKUP_PATH): str,
            }),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_RESTORE_CONFIG):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RESTORE_CONFIG,
            handle_restore_config,
            schema=vol.Schema({
                vol.Required(ATTR_DEVICE_ID): str,
                vol.Optional(ATTR_BACKUP_PATH): str,
            }),
        )


class ShellyBackupCoordinator:
    """Class to manage Shelly script backups."""

    def __init__(
            self,
            hass: HomeAssistant,
            url: str,
            password: str | None,
            backup_path: str
    ) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.url = url
        self.password = password
        self.backup_path = backup_path

        # State tracking
        self.device_id: str | None = None
        self.device_name: str | None = None
        self.last_backup_time: datetime | None = None
        self.last_seen: datetime | None = None
        self.is_available: bool = False
        self.backup_count: int = 0
        self.script_count: int = 0
        self.last_error: str | None = None

    def _update_entities(self) -> None:
        """Trigger entity state updates via dispatcher."""
        if self.device_id:
            async_dispatcher_send(
                self.hass,
                SIGNAL_UPDATE_SHELLY.format(self.device_id)
            )

    async def update_device_status(self) -> bool:
        """Update device availability status."""
        try:
            async with ShellyClient(self.url, self.password) as client:
                device_info = await client.get_device_info()
                self.device_id = device_info.get("id", "unknown")
                self.device_name = device_info.get("name", "unknown")
                self.last_seen = dt_util.utcnow()
                self.is_available = True
                self.last_error = None

            # Update entity states
            self._update_entities()
            return True
        except Exception as err:
            _LOGGER.warning(f"Failed to update device status: {err}")
            self.is_available = False
            self.last_error = str(err)

            # Update entity states
            self._update_entities()
            return False

    async def backup_scripts(self) -> None:
        """Backup all scripts from the device."""
        try:
            # Update device status first
            if not await self.update_device_status():
                _LOGGER.error("Device is offline, skipping backup")
                return

            _LOGGER.info(f"Starting backup for device {self.device_name} ({self.device_id})")

            # Create device-specific backup directory
            device_backup_path = Path(self.backup_path) / self.device_id
            device_backup_path.mkdir(parents=True, exist_ok=True)

            async with ShellyClient(self.url, self.password) as client:
                # Backup device configuration
                await self._backup_config(client, device_backup_path, self.device_id, self.device_name)

                # Backup scripts
                scripts_response = await client.get_script_list()
                scripts = scripts_response.get("scripts", [])
                self.script_count = len(scripts)

                if not scripts:
                    _LOGGER.info(f"No scripts found on device {self.device_id}")
                else:
                    # Backup each script
                    backed_up_count = 0
                    for script in scripts:
                        script_id = script.get("id")
                        script_name = script.get("name", f"script_{script_id}")

                        _LOGGER.debug(f"Backing up script {script_name} (ID: {script_id})")

                        try:
                            code_response = await client.get_script_code(script_id)
                            code = code_response.get("data", "")

                            # Save script code
                            script_file = device_backup_path / f"{script_id}_{script_name}.js"
                            with open(script_file, "w", encoding="utf-8") as f:
                                f.write(code)

                            # Save script metadata
                            metadata = {
                                "id": script_id,
                                "name": script_name,
                                "enable": script.get("enable", False),
                                "device_id": self.device_id,
                                "device_name": self.device_name,
                            }

                            metadata_file = device_backup_path / f"{script_id}_{script_name}.json"
                            with open(metadata_file, "w", encoding="utf-8") as f:
                                json.dump(metadata, f, indent=2)

                            _LOGGER.info(f"Backed up script {script_name} (ID: {script_id})")
                            backed_up_count += 1
                        except Exception as err:
                            _LOGGER.error(f"Error backing up script {script_name}: {err}")

            # Update backup metrics (use timezone-aware datetime)
            self.last_backup_time = dt_util.utcnow()
            self.backup_count += 1
            self.last_error = None

            # Update entity states
            self._update_entities()

            _LOGGER.info(f"Backup completed for device {self.device_id}")

        except Exception as err:
            _LOGGER.error(f"Error during backup: {err}")
            self.last_error = str(err)
            self._update_entities()
            raise

    async def _backup_config(
            self,
            client: ShellyClient,
            device_backup_path: Path,
            device_id: str,
            device_name: str
    ) -> None:
        """Backup device configuration."""
        try:
            _LOGGER.debug(f"Backing up configuration for device {device_id}")

            config = await client.get_config()

            # Save full configuration
            config_file = device_backup_path / "device_config.json"
            config_data = {
                "device_id": device_id,
                "device_name": device_name,
                "config": config,
                "backup_time": dt_util.utcnow().isoformat(),
            }

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)

            _LOGGER.info(f"Backed up configuration for device {device_id}")

        except Exception as err:
            _LOGGER.error(f"Error backing up configuration: {err}")
            # Don't raise - continue with script backup even if config backup fails

    async def restore_script(self, script_id: int, backup_path: str | None = None) -> None:
        """Restore a script from backup."""
        try:
            if not await self.update_device_status():
                _LOGGER.error("Device is offline, cannot restore script")
                return

            if backup_path:
                script_file = Path(backup_path)
            else:
                # Find the script in the default backup location
                device_backup_path = Path(self.backup_path) / self.device_id
                script_files = list(device_backup_path.glob(f"{script_id}_*.js"))

                if not script_files:
                    _LOGGER.error(f"No backup found for script ID {script_id}")
                    return

                script_file = script_files[0]

            # Read script code
            with open(script_file, "r", encoding="utf-8") as f:
                code = f.read()

            # Upload to device
            _LOGGER.info(f"Restoring script ID {script_id} from {script_file}")
            async with ShellyClient(self.url, self.password) as client:
                await client.put_script_code(script_id, code)
            _LOGGER.info(f"Script ID {script_id} restored successfully")

        except Exception as err:
            _LOGGER.error(f"Error restoring script: {err}")
            raise

    async def restore_config(self, backup_path: str | None = None) -> None:
        """Restore device configuration from backup."""
        try:
            if not await self.update_device_status():
                _LOGGER.error("Device is offline, cannot restore configuration")
                return

            if backup_path:
                config_file = Path(backup_path)
            else:
                # Use default backup location
                device_backup_path = Path(self.backup_path) / self.device_id
                config_file = device_backup_path / "device_config.json"

            if not config_file.exists():
                _LOGGER.error(f"No configuration backup found at {config_file}")
                return

            # Read configuration
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            config = config_data.get("config", {})

            # Restore configuration to device
            _LOGGER.info(f"Restoring configuration from {config_file}")
            async with ShellyClient(self.url, self.password) as client:
                await client.set_config(config)
            _LOGGER.info(f"Configuration restored successfully for device {self.device_id}")

        except Exception as err:
            _LOGGER.error(f"Error restoring configuration: {err}")
            raise
