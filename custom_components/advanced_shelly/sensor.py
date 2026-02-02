"""Sensor platform for Shelly Scripts Backup."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from . import SIGNAL_UPDATE_SHELLY


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Shelly backup sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        ShellyLastBackupSensor(coordinator, entry),
        ShellyScriptCountSensor(coordinator, entry),
    ])


class ShellyLastBackupSensor(SensorEntity):
    """Sensor showing the last backup timestamp."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_last_backup"
        self._attr_name = "Last backup"

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        @callback
        def update():
            self.async_write_ha_state()

        if self._coordinator.device_id:
            self.async_on_remove(
                async_dispatcher_connect(
                    self.hass,
                    SIGNAL_UPDATE_SHELLY.format(self._coordinator.device_id),
                    update
                )
            )

    @property
    def native_value(self) -> datetime | None:
        """Return the last backup time."""
        return self._coordinator.last_backup_time

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"Shelly Device {self._coordinator.device_name or self._entry.entry_id}",
            "manufacturer": "Shelly",
            "model": "Script Backup",
        }

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "device_id": self._coordinator.device_id,
            "backup_count": self._coordinator.backup_count,
            "last_error": self._coordinator.last_error,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.is_available


class ShellyScriptCountSensor(SensorEntity):
    """Sensor showing the number of scripts on device."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:script-text"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_script_count"
        self._attr_name = "Script count"
        self._attr_native_unit_of_measurement = "scripts"

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        @callback
        def update():
            self.async_write_ha_state()

        if self._coordinator.device_id:
            self.async_on_remove(
                async_dispatcher_connect(
                    self.hass,
                    SIGNAL_UPDATE_SHELLY.format(self._coordinator.device_id),
                    update
                )
            )

    @property
    def native_value(self) -> int | None:
        """Return the script count."""
        return self._coordinator.script_count

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"Shelly Device {self._coordinator.device_name or self._entry.entry_id}",
            "manufacturer": "Shelly",
            "model": "Script Backup",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.is_available