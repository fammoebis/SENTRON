from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from pymodbus.client import ModbusTcpClient

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_REGISTER


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    config = entry.data

    sensor = SentronSensor(config)
    async_add_entities([sensor], True)


class SentronSensor(SensorEntity):
    def __init__(self, config):
        self._host = config[CONF_HOST]
        self._port = config[CONF_PORT]
        self._register = config[CONF_REGISTER]
        self._state = None

        self._attr_name = f"SENTRON Register {self._register}"
        self._attr_unique_id = f"sentron_{self._host}_{self._register}"

        self._client = ModbusTcpClient(self._host, port=self._port)

    def update(self):
        try:
            if not self._client.connect():
                self._state = None
                return

            result = self._client.read_holding_registers(self._register, 1)

            if result.isError():
                self._state = None
            else:
                self._state = result.registers[0]

        except Exception:
            self._state = None
        finally:
            self._client.close()

    @property
    def state(self):
        return self._state