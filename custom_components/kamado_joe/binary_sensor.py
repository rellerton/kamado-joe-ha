"""Binary sensor platform for Kamado Joe."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KamadoJoeConfigEntry
from .const import (
    active_errors,
    binary_sensor_keys,
    probe_numbers,
    probe_present,
    probe_reached,
    target_reached,
)
from .entity import KamadoJoeEntity


@dataclass(frozen=True, kw_only=True)
class KamadoJoeBinaryDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], bool | None]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    present_fn: Callable[[dict[str, Any]], bool] | None = None


BINARY_SENSORS: tuple[KamadoJoeBinaryDescription, ...] = (
    KamadoJoeBinaryDescription(
        key="power",
        translation_key="power",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda r: r.get("pwrOn"),
    ),
    KamadoJoeBinaryDescription(
        key="heating",
        translation_key="heating",
        value_fn=lambda r: r.get("heat", {}).get("t2", {}).get("heating"),
    ),
    KamadoJoeBinaryDescription(
        key="problem",
        translation_key="problem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda r: bool(active_errors(r)),
        attrs_fn=lambda r: {"codes": active_errors(r), "raw": r.get("errors")},
    ),
    KamadoJoeBinaryDescription(
        key="high_temperature_alert",
        translation_key="high_temperature_alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda r: bool((r.get("notifications") or {}).get("high_temp")),
    ),
    KamadoJoeBinaryDescription(
        key="low_temperature_alert",
        translation_key="low_temperature_alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda r: bool((r.get("notifications") or {}).get("low_temp")),
    ),
    KamadoJoeBinaryDescription(
        key="target_reached",
        translation_key="target_reached",
        value_fn=target_reached,
    ),
)

PROBE_REACHED: tuple[KamadoJoeBinaryDescription, ...] = tuple(
    KamadoJoeBinaryDescription(
        key=f"probe{n}_reached",
        translation_key=f"probe{n}_reached",
        icon="mdi:thermometer-check",
        value_fn=lambda r, n=n: probe_reached(r, n),
        present_fn=lambda r, n=n: probe_present(r, n),
    )
    for n in (1, 2, 3)
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KamadoJoeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[KamadoJoeEntity] = []
    for mac, metadata in coordinator.devices.items():
        supported_binary_sensors = binary_sensor_keys(metadata.get("model"))
        supported_probes = probe_numbers(metadata.get("model"))
        probe_descriptions = tuple(
            desc
            for desc in PROBE_REACHED
            if any(desc.key.startswith(f"probe{number}_") for number in supported_probes)
        )
        entities.extend(
            KamadoJoeBinarySensor(coordinator, mac, desc)
            for desc in (
                *(
                    desc
                    for desc in BINARY_SENSORS
                    if desc.key in supported_binary_sensors
                ),
                *probe_descriptions,
            )
        )
    entities += [KamadoJoeStaleSensor(coordinator, mac) for mac in coordinator.devices]
    async_add_entities(entities)


class KamadoJoeBinarySensor(KamadoJoeEntity, BinarySensorEntity):
    entity_description: KamadoJoeBinaryDescription

    def __init__(self, coordinator, mac: str, description: KamadoJoeBinaryDescription) -> None:
        super().__init__(coordinator, mac, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.reported)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attrs_fn:
            return self.entity_description.attrs_fn(self.reported)
        return None

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        present = self.entity_description.present_fn
        return present(self.reported) if present else True


class KamadoJoeStaleSensor(KamadoJoeEntity, BinarySensorEntity):
    """On when the cloud shadow has stopped being updated by the grill.

    This exists because the failure it detects is genuinely misleading: the
    controller can carry on cooking while its WiFi module wedges, and the cloud
    then serves a frozen shadow that eventually reads ``pwrOn: false`` with no
    ``mainTemp``. Every other entity here will calmly report "off". Alert on
    this, not on the power sensor.
    """

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "stale"

    def __init__(self, coordinator, mac: str) -> None:
        super().__init__(coordinator, mac, "stale")

    @property
    def is_on(self) -> bool:
        return self.coordinator.is_stale(self._mac)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "last_reported": self.coordinator.reported_at.get(self._mac),
            "age_seconds": self.coordinator.age(self._mac),
            "threshold_seconds": self.coordinator.stale_after.total_seconds(),
        }
