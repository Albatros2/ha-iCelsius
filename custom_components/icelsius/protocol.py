from __future__ import annotations

import re

_NUMBER_PATTERN = re.compile(r"^-?\d+(?:\.\d+)?$")


class PacketBuffer:
    """Accumulate ampersand-terminated fields from one UDP sender."""

    def __init__(self) -> None:
        self.partial = ""
        self.values: dict[str, str] = {}

    def feed(self, payload: bytes) -> dict[str, str]:
        parts = (self.partial + payload.decode("ascii", errors="replace")).split("&")
        self.partial = parts.pop()
        updates = {}
        for part in parts:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            if key:
                updates[key] = value
        self.values.update(updates)
        return updates


def normalize_value(key: str, value: str):
    if key.startswith("temp") and _NUMBER_PATTERN.match(value):
        return (float(value) - 25000) / 100
    if key == "battery" and _NUMBER_PATTERN.match(value):
        return float(value) / 1000
    if _NUMBER_PATTERN.match(value):
        numeric_value = float(value)
        return int(numeric_value) if numeric_value.is_integer() else numeric_value
    return value