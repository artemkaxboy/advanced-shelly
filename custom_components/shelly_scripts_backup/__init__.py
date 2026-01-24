"""The Shelly Scripts Backup integration."""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import timedelta
from pathlib import Path

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.exceptions import ConfigEntryNotReady
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_BACKUP_PATH,
    CONF_BACKUP_INTERVAL,
    DEFAULT_BACKUP_PATH,
    DEFAULT_BACKUP_INTERVAL,
    SERVICE_BACKUP_NOW,
    SERVICE_RESTORE_SCRIPT,
    ATTR_DEVICE_ID,
    ATTR_SCRIPT_ID,
    ATTR_BACKUP_PATH,
    SHELLY_SCRIPT_LIST,
    SHELLY_SCRIPT_GETCODE,
    SHELLY_SCRIPT_PUTCODE,
    SHELLY_DEVICE_INFO,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Shelly Scripts Backup from a config entry."""
    host = entry.data[CONF_HOST]
    backup_path = entry.data.get(CONF_BACKUP_PATH, DEFAULT_BACKUP_PATH)
    backup_interval = entry.data.get(CONF_BACKUP_INTERVAL, DEFAULT_BACKUP_INTERVAL)

    # Create backup directory if it doesn't exist
    Path(backup_path).mkdir(parents=True, exist_ok=True)

    # Initialize the coordinator
    coordinator = ShellyBackupCoordinator(hass, host, backup_path)
    
    # Test connection
    try:
        await coordinator.get_device_info()
    except Exception as err:
        _LOGGER.error("Failed to connect to Shelly device: %s", err)
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

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Cancel the periodic backup
    cancel_interval = hass.data[DOMAIN].pop(f"{entry.entry_id}_cancel", None)
    if cancel_interval:
        cancel_interval()

    hass.data[DOMAIN].pop(entry.entry_id)

    return True


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Shelly Scripts Backup."""

    async def handle_backup_now(call: ServiceCall) -> None:
        """Handle manual backup service call."""
        device_id = call.data.get(ATTR_DEVICE_ID)
        
        if device_id:
            # Backup specific device
            for entry_id, coordinator in hass.data[DOMAIN].items():
                if isinstance(coordinator, ShellyBackupCoordinator):
                    info = await coordinator.get_device_info()
                    if info.get("id") == device_id:
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
                info = await coordinator.get_device_info()
                if info.get("id") == device_id:
                    await coordinator.restore_script(script_id, backup_path)
                    return
        
        _LOGGER.error("Device with ID %s not found", device_id)

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


class ShellyBackupCoordinator:
    """Class to manage Shelly script backups."""

    def __init__(self, hass: HomeAssistant, host: str, backup_path: str) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.host = host
        self.backup_path = backup_path
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _make_request(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a request to the Shelly device."""
        url = f"http://{self.host}{endpoint}"
        
        try:
            async with self.session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error making request to %s: %s", url, err)
            raise

    async def get_device_info(self) -> dict:
        """Get device information."""
        return await self._make_request(SHELLY_DEVICE_INFO)

    async def get_scripts_list(self) -> list[dict]:
        """Get list of scripts from the device."""
        response = await self._make_request(SHELLY_SCRIPT_LIST)
        return response.get("scripts", [])

    async def get_script_code(self, script_id: int) -> str:
        """Get script code by ID."""
        response = await self._make_request(SHELLY_SCRIPT_GETCODE, {"id": script_id})
        return response.get("data", "")

    async def put_script_code(self, script_id: int, code: str) -> dict:
        """Upload script code to the device."""
        url = f"http://{self.host}{SHELLY_SCRIPT_PUTCODE}"
        
        try:
            async with self.session.post(
                url,
                json={"id": script_id, "code": code},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error uploading script: %s", err)
            raise

    async def backup_scripts(self) -> None:
        """Backup all scripts from the device."""
        try:
            device_info = await self.get_device_info()
            device_id = device_info.get("id", "unknown")
            device_name = device_info.get("name", "unknown")
            
            _LOGGER.info("Starting backup for device %s (%s)", device_name, device_id)

            scripts = await self.get_scripts_list()
            
            if not scripts:
                _LOGGER.info("No scripts found on device %s", device_id)
                return

            # Create device-specific backup directory
            device_backup_path = Path(self.backup_path) / device_id
            device_backup_path.mkdir(parents=True, exist_ok=True)

            # Backup each script
            for script in scripts:
                script_id = script.get("id")
                script_name = script.get("name", f"script_{script_id}")
                
                _LOGGER.debug("Backing up script %s (ID: %s)", script_name, script_id)
                
                try:
                    code = await self.get_script_code(script_id)
                    
                    # Save script code
                    script_file = device_backup_path / f"{script_id}_{script_name}.js"
                    with open(script_file, "w", encoding="utf-8") as f:
                        f.write(code)
                    
                    # Save script metadata
                    metadata = {
                        "id": script_id,
                        "name": script_name,
                        "enable": script.get("enable", False),
                        "device_id": device_id,
                        "device_name": device_name,
                    }
                    
                    metadata_file = device_backup_path / f"{script_id}_{script_name}.json"
                    with open(metadata_file, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2)
                    
                    _LOGGER.info(
                        "Backed up script %s (ID: %s) to %s",
                        script_name,
                        script_id,
                        script_file,
                    )
                except Exception as err:
                    _LOGGER.error("Error backing up script %s: %s", script_name, err)

            _LOGGER.info("Backup completed for device %s", device_id)

        except Exception as err:
            _LOGGER.error("Error during backup: %s", err)
            raise

    async def restore_script(self, script_id: int, backup_path: str | None = None) -> None:
        """Restore a script from backup."""
        try:
            device_info = await self.get_device_info()
            device_id = device_info.get("id", "unknown")

            if backup_path:
                script_file = Path(backup_path)
            else:
                # Find the script in the default backup location
                device_backup_path = Path(self.backup_path) / device_id
                script_files = list(device_backup_path.glob(f"{script_id}_*.js"))
                
                if not script_files:
                    _LOGGER.error("No backup found for script ID %s", script_id)
                    return
                
                script_file = script_files[0]

            # Read script code
            with open(script_file, "r", encoding="utf-8") as f:
                code = f.read()

            # Upload to device
            _LOGGER.info("Restoring script ID %s from %s", script_id, script_file)
            await self.put_script_code(script_id, code)
            _LOGGER.info("Script ID %s restored successfully", script_id)

        except Exception as err:
            _LOGGER.error("Error restoring script: %s", err)
            raise

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
