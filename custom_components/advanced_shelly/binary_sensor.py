"""Binary sensor platform for Shelly Scripts Backup."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
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
    """Set up Shelly backup binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        ShellyDeviceConnectivitySensor(coordinator, entry),
    ])


class ShellyDeviceConnectivitySensor(BinarySensorEntity):
    """Binary sensor showing device online/offline status."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_connectivity"
        self._attr_name = "Connectivity"

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
    def is_on(self) -> bool:
        """Return true if device is online."""
        return self._coordinator.is_available

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
            "last_seen": self._coordinator.last_seen,
            "device_id": self._coordinator.device_id,
        }