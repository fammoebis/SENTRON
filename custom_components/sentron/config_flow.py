import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_REGISTER

class SentronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"SENTRON {user_input[CONF_HOST]}",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=502): int,
            vol.Required(CONF_REGISTER, default=0): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema)