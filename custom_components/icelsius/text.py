from __future__ import annotations

from homeassistant.components.text import TextEntity
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
            async_add_entities([ICelsiusSSIDText(runtime, sensor_id)])

    for sensor_id in runtime.devices:
        discover(sensor_id)
    entry.async_on_unload(runtime.subscribe(discover))


class ICelsiusSSIDText(TextEntity):
    _attr_has_entity_name = True
    _attr_name = "Wi-Fi SSID"
    _attr_native_max = 32
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = "text"

    def __init__(self, runtime: ICelsiusRuntime, sensor_id: str) -> None:
        self.runtime = runtime
        self.sensor_id = sensor_id
        self._value = ""
        self._attr_unique_id = f"{sensor_id}_ssid"

    @property
    def native_value(self) -> str:
        return self.runtime.devices.get(self.sensor_id, {}).get(
            "ChangeSSID", self._value
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.sensor_id)},
            name=f"iCelsius {self.sensor_id}",
            manufacturer="iCelsius",
        )

    async def async_set_value(self, value: str) -> None:
        try:
            await self.runtime.send_command(self.sensor_id, "ChangeSSID", value)
        except (OSError, RuntimeError) as err:
            raise HomeAssistantError(f"Could not change Wi-Fi SSID: {err}") from err
        self._value = value
        self.async_write_ha_state()