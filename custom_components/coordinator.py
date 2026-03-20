from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

_LOGGER = logging.getLogger(__name__)


class SentronCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client):
        super().__init__(
            hass,
            _LOGGER,
            name="sentron",
            update_interval=timedelta(seconds=10),
        )
        self.client = client

    async def _async_update_data(self):
        data = {}

        registers = {
            "energy_in": (801, "float64", 0.001),
            "energy_out": (809, "float64", 0.001),
            "power": (65, "float32", 1.0),
        }

        try:
            if not self.client.connected:
                await self.client.connect()

            for key, (address, dtype, scale) in registers.items():
                count = 4 if dtype == "float64" else 2
                result = await self.client.read_input_registers(address, count, slave=1)

                if result.isError():
                    data[key] = None
                    continue

                decoder = BinaryPayloadDecoder.fromRegisters(
                    result.registers,
                    byteorder=Endian.BIG,
                    wordorder=Endian.BIG,
                )

                value = (
                    decoder.decode_64bit_float()
                    if dtype == "float64"
                    else decoder.decode_32bit_float()
                )

                data[key] = round(value * scale, 2)

        except Exception as err:
            _LOGGER.warning("Update failed: %s", err)
            raise

        return data