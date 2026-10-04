# iCelsius for Home Assistant

[![Open your Home Assistant instance and show the integration inside HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Albatros2&repository=ha-iCelsius&category=integration)

This custom integration receives iCelsius sensor packets over UDP and exposes
temperature, battery voltage, and signal strength in Home Assistant. It also
provides entities to change the sampling interval and Wi-Fi SSID.

## Installation

1. Copy `custom_components/icelsius` into the Home Assistant `custom_components`
   directory, or add this repository to HACS as a custom integration.
2. Restart Home Assistant and add **iCelsius** from **Settings > Devices & services**.
3. Enter the UDP port that the sensor sends its data to (default `54521`).
4. Configure the sensor to send its UDP telemetry to the Home Assistant host and
   that port. Allow inbound UDP traffic through the host firewall.

The thermometer must be configured to send telemetry to Home Assistant's IP and
the selected UDP port; being connected to the same network alone is not enough
for discovery. If no device appears, enable debug logging for
`custom_components.icelsius` and check that packets reach this port.

The integration discovers each sensor from its `SensorID` field. Temperature
fields use the FHEM conversion `(raw - 25000) / 100`; battery values are exposed
as volts (`raw / 1000`). The sampling interval command is sent to the sensor's
source IP on UDP port `54521`.

## Versioning Strategy

Integration versions and Git tags use calendar versioning:

- First release of a day: `YYYY.M.D` (for example, `2026.10.4`)
- Additional releases on the same day: `YYYY.M.D.N` (for example, `2026.10.4.1`)
- Git tags add a `v` prefix, such as `v2026.10.4` or `v2026.10.4.1`

To publish a release, run **Actions > Release > Run workflow** on the `main`
branch. The workflow updates the integration version, pushes the release commit
and tag, and creates a GitHub release with generated notes.