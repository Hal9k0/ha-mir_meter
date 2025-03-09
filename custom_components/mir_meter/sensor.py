"""Support for MIR meter sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import update_coordinator
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_TYPES, MirMeterSensorEntityDescription
from .coordinator import MIRMeterCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        IammeterSensor(coordinator, description) for description in SENSOR_TYPES
    )


class IammeterSensor(update_coordinator.CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    entity_description: MirMeterSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MIRMeterCoordinator,
        description: MirMeterSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.unique_id)},
            name=f"МИР {coordinator.name}",
            manufacturer='НПО "МИР"',
            model=coordinator.name[0 : coordinator.name.find("-")],
        )

    @property
    def native_value(self):
        """Return the native sensor value."""
        raw_attr = self.coordinator.data.get(self.entity_description.key, None)
        if raw_attr is not None:
            raw_attr = raw_attr[2]
            if self.entity_description.value:
                return self.entity_description.value(raw_attr)
        return raw_attr
