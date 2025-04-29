"""mir_meter Coordinator."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from bleak.exc import BleakError
from mirmeter.client import MIRMeter

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MIRMeterCoordinator(DataUpdateCoordinator[dict[int, dict[str, Any]]]):
    """Coordinator is responsible for querying the device at a specified route."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, mir_meter: MIRMeter) -> None:
        """Initialize the data object."""
        super().__init__(hass, _LOGGER, name="MIRMeter", update_interval=SCAN_INTERVAL)
        self.unique_id = entry.entry_id
        self.name = entry.title
        self.mir_meter = mir_meter
        self.data = {}
        self.full_poll = True

    async def _async_update_data(self):
        """Update the data from the device."""
        data = {}
        for _ in range(3):
            try:
                data = await self.mir_meter.get_data(self.full_poll)
                self.full_poll = False
            except (BleakError, TimeoutError, ConnectionError, InterruptedError):
                await asyncio.sleep(2)
                continue
            break

        if not data:
            raise UpdateFailed

        self.data.update(data)
        _LOGGER.debug("Connection to MIR meter successful. Retrieved latest data")
        return self.data
