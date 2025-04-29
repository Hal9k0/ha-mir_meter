"""The mir_meter integration."""

from __future__ import annotations

import logging

from mirmeter.client import MIRMeter

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_PIN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MIRMeterCoordinator

_LOGGER = logging.getLogger(__name__)

_PLATFORMS: list[Platform] = [Platform.SENSOR]

type MIRMeterConfigEntry = ConfigEntry[MIRMeter]


async def async_setup_entry(hass: HomeAssistant, config_entry: MIRMeterConfigEntry) -> bool:
    """Set up mir_meter from a config entry."""
    address = config_entry.data[CONF_MAC]
    ble_device = bluetooth.async_ble_device_from_address(hass, address, True)
    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find MIR meter BLE device with address {address}")

    bleak_scanner = bluetooth.async_get_scanner(hass)
    mir_meter = MIRMeter(bleak_scanner, ble_device, config_entry.data[CONF_PIN])
    coordinator = MIRMeterCoordinator(hass, config_entry, mir_meter)

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(config_entry, _PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: MIRMeterConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, _PLATFORMS)
