import voluptuous as vol
from homeassistant import config_entries
from pymodbus.client import AsyncModbusTcpClient

from .const import DOMAIN


class SentronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                client = AsyncModbusTcpClient(user_input["host"], port=user_input["port"])
                await client.connect()
                await client.close()
            except Exception:
                errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(
                    title=user_input["name"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name", default="SENTRON"): str,
                vol.Required("host"): str,
                vol.Required("port", default=502): int,
            }),
            errors=errors,
        )
