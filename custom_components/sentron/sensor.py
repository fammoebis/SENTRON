from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SentronCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]

    coordinator = SentronCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    data["coordinator"] = coordinator

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.data["name"],
        manufacturer="Siemens",
        model="SENTRON PAC",
    )

    sensors = [
        SentronSensor(coordinator, "energy_in", "Bezogene Energie", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, device_info),
        SentronSensor(coordinator, "energy_out", "Abgegebene Energie", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, device_info),
        SentronSensor(coordinator, "power", "Leistung", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, device_info),
    ]

    async_add_entities(sensors)


class SentronSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit, device_class, state_class, device_info):
        super().__init__(coordinator)

        self._key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_device_info = device_info
        self._attr_unique_id = f"sentron_{coordinator.config_entry.entry_id}_{key}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)