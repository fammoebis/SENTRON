from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from pymodbus.client import AsyncModbusTcpClient

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    client = AsyncModbusTcpClient(entry.data["host"], port=entry.data["port"])
    await client.connect()

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = hass.data[DOMAIN].pop(entry.entry_id)
    client = data["client"]

    await client.close()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)