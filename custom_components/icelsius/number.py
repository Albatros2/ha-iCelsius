from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ICelsiusRuntime
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    runtime: ICelsiusRuntime = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    def discover(sensor_id: str) -> None:
        if sensor_id not in added:
            added.add(sensor_id)
            async_add_entities([ICelsiusSamplingNumber(runtime, sensor_id)])

    for sensor_id in runtime.devices:
        discover(sensor_id)
    entry.async_on_unload(runtime.subscribe(discover))


class ICelsiusSamplingNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Sampling interval"
    _attr_native_min_value = 5
    _attr_native_max_value = 3600
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "s"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, runtime: ICelsiusRuntime, sensor_id: str) -> None:
        self.runtime = runtime
        self.sensor_id = sensor_id
        self._value: int | None = None
        self._attr_unique_id = f"{sensor_id}_sampling"

    @property
    def native_value(self) -> int | None:
        device = self.runtime.devices.get(self.sensor_id, {})
        return device.get("ChangeSampling", self._value)

    @property
    def should_poll(self) -> bool:
        return False

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.runtime.subscribe(self._handle_update))

    def _handle_update(self, sensor_id: str) -> None:
        if sensor_id == self.sensor_id:
            self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.sensor_id)},
            name=f"iCelsius {self.sensor_id}",
            manufacturer="iCelsius",
        )

    async def async_set_native_value(self, value: float) -> None:
        sampling = int(value)
        try:
            await self.runtime.send_sampling(self.sensor_id, sampling)
        except (OSError, RuntimeError) as err:
            raise HomeAssistantError(f"Could not set sampling interval: {err}") from err
        self._value = sampling
        self.async_write_ha_state()