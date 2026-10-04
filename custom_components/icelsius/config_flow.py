from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from .const import DEFAULT_PORT, DOMAIN


class ICelsiusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            port = user_input[CONF_PORT]
            await self.async_set_unique_id(str(port))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"iCelsius UDP {port}", data={CONF_PORT: port}
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    int, vol.Range(min=1, max=65535)
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)