DOMAIN = "icelsius"
PLATFORMS = ["sensor", "number"]

CONF_PORT = "port"
DEFAULT_PORT = 54520
SENSOR_COMMAND_PORT = 54521

SENSOR_DESCRIPTIONS = {
    "temp1": ("Temperature 1", "temperature", "°C"),
    "temp2": ("Temperature 2", "temperature", "°C"),
    "battery": ("Battery voltage", "voltage", "V"),
    "RSSI": ("Signal strength", "signal_strength", "dBm"),
}