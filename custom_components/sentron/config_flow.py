import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from .const import DOMAIN, CONF_AREA

class SentronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME], 
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default="SENTRON"): str,
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=502): int,
                vol.Optional(CONF_AREA): str,
            })
        )