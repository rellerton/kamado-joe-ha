"""Privacy-safe diagnostics for the Kamado Joe integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import KamadoJoeConfigEntry
from .const import CONF_PASSWORD

_REDACT_CONFIG = {CONF_PASSWORD, "email", "devices"}
_REDACT_DEVICE = {
    "mac",
    "macAddress",
    "ssid",
    "userId",
    "thingName",
    "thing_name",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: KamadoJoeConfigEntry
) -> dict[str, Any]:
    """Return state useful for support without account or network identifiers."""
    coordinator = entry.runtime_data
    devices: list[dict[str, Any]] = []

    for mac, metadata in coordinator.devices.items():
        devices.append(
            {
                "metadata": async_redact_data(metadata, _REDACT_DEVICE),
                "reported": async_redact_data(
                    (coordinator.data or {}).get(mac, {}), _REDACT_DEVICE
                ),
                "reported_at": coordinator.reported_at.get(mac),
                "age_seconds": coordinator.age(mac),
                "stale": coordinator.is_stale(mac),
                "current_cook": coordinator.cook.get(mac, {}),
                "last_cook_summary": {
                    key: value
                    for key, value in coordinator.last_cook.get(mac, {}).items()
                    if key != "series"
                },
            }
        )

    return {
        "config_entry": {
            "data": async_redact_data(dict(entry.data), _REDACT_CONFIG),
            "options": async_redact_data(dict(entry.options), _REDACT_CONFIG),
        },
        "devices": devices,
    }
