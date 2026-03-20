import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower, CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.helpers.entity import DeviceInfo

# Hier lag der Fehler in Zeile 5 - Wir nutzen nun den vollen Pfad
from custom_components.sentron.const import DOMAIN, CONF_AREA 

# Pymodbus Importe absichern
try:
    from pymodbus.client import AsyncModbusTcpClient
    from pymodbus.payload import BinaryPayloadDecoder
    from pymodbus.constants import Endian
except ImportError:
    from pymodbus.client.asynchronous.tcp import AsyncModbusTcpClient
    from pymodbus.payload import BinaryPayloadDecoder
    from pymodbus.constants import Endian

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    config = entry.data
    client = AsyncModbusTcpClient(config[CONF_HOST], port=config[CONF_PORT])
    
    device_info = DeviceInfo(
        identifiers={(DOMAIN, f"{config[CONF_HOST]}_{config[CONF_PORT]}")},
        name=config[CONF_NAME],
        manufacturer="Siemens",
        model="SENTRON PAC",
        sw_version="1.3.0",
        suggested_area=config.get(CONF_AREA),
    )
    
    sensors = [
        SentronPACSensor(client, "Bezogene Gesamtwirkenergie Grid", 801, "float64", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, 0.001, device_info),
        SentronPACSensor(client, "Abgegebene Gesamtwirkenergie Grid", 809, "float64", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, 0.001, device_info),
        SentronPACSensor(client, "Wirkleistung Grid", 65, "float32", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, 1.0, device_info)
    ]
    async_add_entities(sensors, True)

class SentronPACSensor(SensorEntity):
    def __init__(self, client, name, address, data_type, unit, device_class, state_class, scale, device_info):
        self._client = client
        self._attr_name = name
        self._address = address
        self._data_type = data_type
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._scale = scale
        self._attr_device_info = device_info
        self._attr_unique_id = f"sentron_{device_info['identifiers'].copy().pop()[1]}_{address}"

    async def async_update(self):
        try:
            if not self._client.connected:
                await self._client.connect()
            
            count = 4 if self._data_type == "float64" else 2
            result = await self._client.read_input_registers(self._address, count, slave=1)
            
            if not result.isError():
                decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
                val = decoder.decode_64bit_float() if self._data_type == "float64" else decoder.decode_32bit_float()
                self._attr_native_value = round(val * self._scale, 1)
        except Exception as e:
            _LOGGER.debug("Update Fehler: %s", e)
            self._attr_native_value = None