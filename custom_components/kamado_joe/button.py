"""Manual refresh button for Kamado Joe cloud data."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KamadoJoeConfigEntry
from .entity import KamadoJoeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KamadoJoeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one device-scoped refresh button per grill."""
    coordinator = entry.runtime_data
    async_add_entities(
        KamadoJoeRefreshButton(coordinator, mac) for mac in coordinator.devices
    )


class KamadoJoeRefreshButton(KamadoJoeEntity, ButtonEntity):
    """Request an immediate cloud refresh outside the adaptive poll schedule."""

    _attr_icon = "mdi:cloud-refresh"
    _attr_translation_key = "refresh"

    def __init__(self, coordinator, mac: str) -> None:
        super().__init__(coordinator, mac, "refresh")

    async def async_press(self) -> None:
        """Refresh every grill managed by this config entry immediately."""
        await self.coordinator.async_request_refresh()
