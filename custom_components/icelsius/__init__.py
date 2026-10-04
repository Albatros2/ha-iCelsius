from __future__ import annotations

import asyncio
import logging
import socket
from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, SENSOR_COMMAND_PORT
from .protocol import PacketBuffer, normalize_value

_LOGGER = logging.getLogger(__name__)


class ICelsiusProtocol(asyncio.DatagramProtocol):
    def __init__(self, runtime: "ICelsiusRuntime") -> None:
        self.runtime = runtime

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        _LOGGER.debug(
            "Received %s bytes from iCelsius sender %s:%s",
            len(data),
            addr[0],
            addr[1],
        )
        peer = self.runtime.peers.setdefault(addr, PacketBuffer())
        updates = peer.feed(data)
        sensor_id = peer.values.get("SensorID")
        if not sensor_id:
            _LOGGER.debug(
                "Waiting for a complete iCelsius SensorID from %s:%s",
                addr[0],
                addr[1],
            )
            return

        if sensor_id not in self.runtime.devices:
            _LOGGER.debug("Discovered iCelsius sensor %s from %s", sensor_id, addr[0])
        device = self.runtime.devices.setdefault(sensor_id, {})
        device["ip"] = addr[0]
        for key, value in peer.values.items():
            device[key] = normalize_value(key, value)
        for listener in tuple(self.runtime.listeners):
            listener(sensor_id)


class ICelsiusRuntime:
    def __init__(self, port: int) -> None:
        self.port = port
        self.devices: dict[str, dict] = {}
        self.peers: dict[tuple[str, int], PacketBuffer] = {}
        self.listeners: set[Callable[[str], None]] = set()
        self.transport: asyncio.DatagramTransport | None = None

    async def start(self) -> None:
        loop = asyncio.get_running_loop()
        try:
            transport, _ = await loop.create_datagram_endpoint(
                lambda: ICelsiusProtocol(self), local_addr=("0.0.0.0", self.port)
            )
        except OSError as err:
            raise RuntimeError(f"Could not bind UDP port {self.port}: {err}") from err
        self.transport = transport

    def subscribe(self, listener: Callable[[str], None]) -> Callable[[], None]:
        self.listeners.add(listener)
        return lambda: self.listeners.discard(listener)

    async def send_sampling(self, sensor_id: str, value: int) -> None:
        device = self.devices.get(sensor_id)
        if device is None or "ip" not in device:
            raise RuntimeError("No packet has been received from this sensor yet")

        loop = asyncio.get_running_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        try:
            await loop.sock_sendto(
                sock,
                f"ChangeSampling={value}".encode("ascii"),
                (device["ip"], SENSOR_COMMAND_PORT),
            )
        finally:
            sock.close()

    async def send_command(self, sensor_id: str, command: str, value: str) -> None:
        device = self.devices.get(sensor_id)
        if device is None or "ip" not in device:
            raise RuntimeError("No packet has been received from this sensor yet")

        loop = asyncio.get_running_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        try:
            await loop.sock_sendto(
                sock,
                f"{command}={value}".encode("utf-8"),
                (device["ip"], SENSOR_COMMAND_PORT),
            )
        finally:
            sock.close()

    async def stop(self) -> None:
        if self.transport is not None:
            self.transport.close()
            self.transport = None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    runtime = ICelsiusRuntime(entry.options.get(CONF_PORT, entry.data[CONF_PORT]))
    try:
        await runtime.start()
    except RuntimeError as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime
    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform.SENSOR, Platform.NUMBER, Platform.TEXT]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(
        entry, [Platform.SENSOR, Platform.NUMBER, Platform.TEXT]
    )
    if unloaded:
        runtime: ICelsiusRuntime = hass.data[DOMAIN][entry.entry_id]
        await runtime.stop()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded