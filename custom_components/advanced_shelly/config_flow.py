"""Config flow for Advanced Shelly integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .shelly_client import ShellyClient
from .const import (
    DOMAIN,
    CONF_URL,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_BACKUP_PATH,
    CONF_BACKUP_INTERVAL,
    DEFAULT_BACKUP_PATH,
    DEFAULT_BACKUP_INTERVAL,
    DEFAULT_NAME,
    SHELLY_USERNAME,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    url = data[CONF_URL]
    password = data.get(CONF_PASSWORD, "")

    try:
        _LOGGER.debug(f"Connecting to Shelly device at {url}")
        async with ShellyClient(url, password) as client:

            _LOGGER.debug("Getting device info")
            device_info = await client.get_device_info()
            _LOGGER.debug(f"Device info: {device_info}")

            # Check if device supports scripts (Gen2+ devices)
            if "gen" not in device_info:
                raise UnsupportedDevice("Device does not report generation (might be Gen1)")

            if device_info.get("gen") < 2:
                raise UnsupportedDevice(f"Device is Gen{device_info.get('gen')}, scripts require Gen2+")

            device_id = device_info.get("id", "unknown")
            device_model = device_info.get("model", "unknown")
            _LOGGER.info(f"Successfully validated Shelly device: {url} (ID: {device_id}, Model: {device_model})")

            # Test authentication by fetching status
            _ = await client.get_status()
            return {
                "title": url,
                "device_id": device_id,
                "model": device_model,
            }

    except aiohttp.ClientError as err:
        _LOGGER.error(f"Error connecting to Shelly device: {err}")
        raise CannotConnect(f"Connection error: {err}") from err
    except (KeyError, ValueError, TypeError) as err:
        _LOGGER.error(f"Error parsing device response: {err}")
        raise CannotConnect(f"Invalid device response: {err}") from err


class AdvancedShellyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Advanced Shelly."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
            config_entry: config_entries.ConfigEntry,
    ) -> AdvancedShellyOptionsFlow:
        """Get the options flow for this handler."""
        return AdvancedShellyOptionsFlow(config_entry)

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
                vol.Required(CONF_URL): str,
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


class AdvancedShellyOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Advanced Shelly integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update config entry data with new values
            new_data = {**self._config_entry.data}
            new_data[CONF_BACKUP_INTERVAL] = user_input[CONF_BACKUP_INTERVAL]
            new_data[CONF_BACKUP_PATH] = user_input[CONF_BACKUP_PATH]

            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data=new_data,
            )

            return self.async_create_entry(title="", data={})

        current_backup_interval = self._config_entry.data.get(
            CONF_BACKUP_INTERVAL, DEFAULT_BACKUP_INTERVAL
        )
        current_backup_path = self._config_entry.data.get(
            CONF_BACKUP_PATH, DEFAULT_BACKUP_PATH
        )

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_BACKUP_INTERVAL,
                    default=current_backup_interval
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=3600,
                        max=604800,
                        step=3600,
                        unit_of_measurement="seconds",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_BACKUP_PATH,
                    default=current_backup_path
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate authentication failed."""


class UnsupportedDevice(HomeAssistantError):
    """Error to indicate device doesn't support scripts."""
