# iCelsius for Home Assistant

This custom integration receives iCelsius sensor packets over UDP and exposes
temperature, battery voltage, and signal strength in Home Assistant. It also
provides entities to change the sampling interval and Wi-Fi SSID.

## Installation

1. Copy `custom_components/icelsius` into the Home Assistant `custom_components`
   directory, or add this repository to HACS as a custom integration.
2. Restart Home Assistant and add **iCelsius** from **Settings > Devices & services**.
3. Enter the UDP port that the sensor sends its data to (default `54520`).
4. Configure the sensor to send its UDP telemetry to the Home Assistant host and
   that port. Allow inbound UDP traffic through the host firewall.

The integration discovers each sensor from its `SensorID` field. Temperature
fields use the FHEM conversion `(raw - 25000) / 100`; battery values are exposed
as volts (`raw / 1000`). The sampling interval command is sent to the sensor's
source IP on UDP port `54521`.