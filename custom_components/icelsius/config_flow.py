from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from .const import DEFAULT_PORT, DOMAIN


class ICelsiusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def _port_schema(self, port: int) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_PORT, default=port): vol.All(
                    int, vol.Range(min=1, max=65535)
                )
            }
        )

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            port = user_input[CONF_PORT]
            await self.async_set_unique_id(str(port))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"iCelsius UDP {port}", data={CONF_PORT: port}
            )

        return self.async_show_form(
            step_id="user", data_schema=self._port_schema(DEFAULT_PORT)
        )

    async def async_step_reconfigure(self, user_input=None):
        entry = self._get_reconfigure_entry()
        errors = {}
        if user_input is not None:
            port = user_input[CONF_PORT]
            duplicate = any(
                other.entry_id != entry.entry_id
                and other.data.get(CONF_PORT) == port
                for other in self.hass.config_entries.async_entries(DOMAIN)
            )
            if duplicate:
                errors[CONF_PORT] = "already_configured"
            else:
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={CONF_PORT: port},
                    title=f"iCelsius UDP {port}",
                    unique_id=str(port),
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self._port_schema(entry.data[CONF_PORT]),
            errors=errors,
        )