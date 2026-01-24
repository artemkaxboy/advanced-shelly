"""Config flow for Advanced Shelly integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_NAME,
    CONF_BACKUP_PATH,
    CONF_BACKUP_INTERVAL,
    DEFAULT_BACKUP_PATH,
    DEFAULT_BACKUP_INTERVAL,
    DEFAULT_NAME,
    SHELLY_DEVICE_INFO,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    
    # Try to connect to the Shelly device
    async with aiohttp.ClientSession() as session:
        try:
            url = f"http://{host}{SHELLY_DEVICE_INFO}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    raise CannotConnect(f"HTTP {response.status}")
                
                device_info = await response.json()
                
                # Check if device supports scripts (Gen2+ devices)
                if "gen" not in device_info or device_info.get("gen") < 2:
                    raise UnsupportedDevice("Device does not support scripts (Gen1 or unknown)")
                
                return {
                    "title": device_info.get("name", data.get(CONF_NAME, DEFAULT_NAME)),
                    "device_id": device_info.get("id", "unknown"),
                    "model": device_info.get("model", "unknown"),
                }
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Shelly device: %s", err)
            raise CannotConnect(f"Connection error: {err}")
        except Exception as err:
            _LOGGER.exception("Unexpected error")
            raise CannotConnect(f"Unexpected error: {err}")


class ShellyScriptsBackupConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shelly Scripts Backup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Set unique ID based on device ID
                await self.async_set_unique_id(info["device_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except UnsupportedDevice:
                errors["base"] = "unsupported_device"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_BACKUP_PATH, default=DEFAULT_BACKUP_PATH): str,
                vol.Optional(
                    CONF_BACKUP_INTERVAL, default=DEFAULT_BACKUP_INTERVAL
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=3600,
                        max=604800,
                        step=3600,
                        unit_of_measurement="seconds",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class UnsupportedDevice(HomeAssistantError):
    """Error to indicate device doesn't support scripts."""
