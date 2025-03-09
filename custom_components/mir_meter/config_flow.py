"""Config flow for mir_meter integration."""

from __future__ import annotations

import logging
from typing import Any

from bleak.backends.device import BLEDevice
from mirmeter.client import MIRMeter
import voluptuous as vol

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_PIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_PIN): cv.positive_int,
    }
)
STEP_PIN_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PIN): cv.positive_int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    scanner_count = bluetooth.async_scanner_count(hass, connectable=True)
    if not scanner_count:
        _LOGGER.error("No bluetooth adapter found")
        raise NoBluetoothAdapter

    bleak_scanner = bluetooth.async_get_scanner(hass)
    mir_meter = MIRMeter(bleak_scanner, data[CONF_NAME], data[CONF_PIN])

    device = await mir_meter.find_device()
    if not device:
        _LOGGER.error("Could not find bluetooth device")
        raise NoDeviceFound

    pin_ok = await mir_meter.check_pin()
    if not pin_ok:
        _LOGGER.error("An incorrect PIN code or meter has blocked you for a while")
        raise InvalidAuth

    return {"title": device.name, "address": device.address}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for mir_meter."""

    VERSION = 1
    _device: BLEDevice

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        _LOGGER.debug("Discovered bluetooth device: %s", discovery_info.as_dict())

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._device = discovery_info.device
        self.context["title_placeholders"] = {"name": self._device.name}

        return await self.async_step_pin()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except NoBluetoothAdapter:
                errors["base"] = "no_bluetooth_adapter"
            except NoDeviceFound:
                errors["base"] = "no_device_found"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["address"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_MAC: info["address"],
                        CONF_PIN: user_input[CONF_PIN],
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_pin(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add a pin code."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                user_input[CONF_NAME] = self._device
                info = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_MAC: info["address"],
                        CONF_PIN: user_input[CONF_PIN],
                    },
                )

        return self.async_show_form(
            step_id="pin",
            data_schema=STEP_PIN_DATA_SCHEMA,
            errors=errors,
            description_placeholders={"display_name": self._device.name},
        )


class NoBluetoothAdapter(HomeAssistantError):
    """Error to indicate no bluetooth adapter could be found."""


class NoDeviceFound(HomeAssistantError):
    """Error to indicate no bluetooth device could be found."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
