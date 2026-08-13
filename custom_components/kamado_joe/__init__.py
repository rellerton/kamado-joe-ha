"""The Kamado Joe integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KamadoJoeApi
from .const import CONF_EMAIL, CONF_PASSWORD
from .coordinator import KamadoJoeCoordinator
from .services import async_register_services

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

type KamadoJoeConfigEntry = ConfigEntry[KamadoJoeCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: KamadoJoeConfigEntry) -> bool:
    """Set up Kamado Joe from a config entry."""
    session = async_get_clientsession(hass)
    api = KamadoJoeApi(session, entry.data[CONF_EMAIL], entry.data[CONF_PASSWORD])
    coordinator = KamadoJoeCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: KamadoJoeConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: KamadoJoeConfigEntry) -> None:
    """Reload when options change (poll interval, staleness, history tracking)."""
    await hass.config_entries.async_reload(entry.entry_id)
