from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ICelsiusRuntime
from .const import DOMAIN, SENSOR_DESCRIPTIONS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    runtime: ICelsiusRuntime = hass.data[DOMAIN][entry.entry_id]
    added: set[tuple[str, str]] = set()

    def discover(sensor_id: str) -> None:
        new_entities = []
        for key in SENSOR_DESCRIPTIONS:
            identity = (sensor_id, key)
            if identity not in added and key in runtime.devices[sensor_id]:
                added.add(identity)
                new_entities.append(ICelsiusSensor(runtime, sensor_id, key))
        if new_entities:
            async_add_entities(new_entities)

    for sensor_id in runtime.devices:
        discover(sensor_id)
    entry.async_on_unload(runtime.subscribe(discover))


class ICelsiusSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, runtime: ICelsiusRuntime, sensor_id: str, key: str) -> None:
        self.runtime = runtime
        self.sensor_id = sensor_id
        self.key = key
        label, device_class, unit = SENSOR_DESCRIPTIONS[key]
        self._attr_name = label
        self._attr_unique_id = f"{sensor_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = SensorDeviceClass(device_class)
        self._attr_state_class = "measurement"
        if key in ("battery", "RSSI"):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def should_poll(self) -> bool:
        return False

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.runtime.subscribe(self._handle_update))

    def _handle_update(self, sensor_id: str) -> None:
        if sensor_id == self.sensor_id:
            self.async_write_ha_state()

    @property
    def native_value(self):
        return self.runtime.devices.get(self.sensor_id, {}).get(self.key)

    @property
    def device_info(self) -> DeviceInfo:
        device = self.runtime.devices.get(self.sensor_id, {})
        sensor_type = device.get("sensorType")
        return DeviceInfo(
            identifiers={(DOMAIN, self.sensor_id)},
            name=f"iCelsius {self.sensor_id}",
            manufacturer="iCelsius",
            model=f"Sensor type {sensor_type}" if sensor_type else None,
        )