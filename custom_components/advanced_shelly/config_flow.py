"""Config flow for Advanced Shelly integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
from aiohttp import DigestAuth
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
    CONF_PASSWORD,
    CONF_BACKUP_PATH,
    CONF_BACKUP_INTERVAL,
    DEFAULT_BACKUP_PATH,
    DEFAULT_BACKUP_INTERVAL,
    DEFAULT_NAME,
    SHELLY_USERNAME,
    SHELLY_DEVICE_INFO,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    password = data.get(CONF_PASSWORD)

    # Prepare auth if password is provided
    auth = None
    if password:
        auth = DigestAuth(SHELLY_USERNAME, password)

    # Try to connect to the Shelly device
    async with aiohttp.ClientSession() as session:
        try:
            url = f"http://{host}{SHELLY_DEVICE_INFO}"
            _LOGGER.debug("Connecting to Shelly device at %s", url)

            async with session.get(
                    url,
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 401:
                    _LOGGER.error("Authentication failed for %s", url)
                    raise InvalidAuth("Authentication required or credentials invalid")

                if response.status != 200:
                    _LOGGER.error("HTTP error %s when connecting to %s", response.status, url)
                    raise CannotConnect(f"HTTP {response.status}")

                device_info = await response.json()
                _LOGGER.debug("Device info: %s", device_info)

                # Check if device supports scripts (Gen2+ devices)
                if "gen" not in device_info:
                    _LOGGER.error("Device does not report generation")
                    raise UnsupportedDevice("Device does not report generation (might be Gen1)")

                if device_info.get("gen") < 2:
                    _LOGGER.error("Device is Gen%s, scripts require Gen2+", device_info.get("gen"))
                    raise UnsupportedDevice(f"Device is Gen{device_info.get('gen')}, scripts require Gen2+")

                device_id = device_info.get("id", "unknown")
                device_model = device_info.get("model", "unknown")

                _LOGGER.info(
                    "Successfully validated Shelly device: %s (ID: %s, Model: %s)",
                    host, device_id, device_model
                )

                return {
                    "title": host,
                    "device_id": device_id,
                    "model": device_model,
                }

        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Shelly device: %s", err)
            raise CannotConnect(f"Connection error: {err}") from err
        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.error("Error parsing device response: %s", err)
            raise CannotConnect(f"Invalid device response: {err}") from err


class AdvancedShellyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advanced Shelly."""

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
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except UnsupportedDevice:
                errors["base"] = "unsupported_device"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_PASSWORD): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD,
                    )
                ),
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


class InvalidAuth(HomeAssistantError):
    """Error to indicate authentication failed."""


class UnsupportedDevice(HomeAssistantError):
    """Error to indicate device doesn't support scripts."""