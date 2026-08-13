"""Tests for payload helpers using sanitized Konnected Joe observations."""
from __future__ import annotations

import json
from pathlib import Path

from custom_components.kamado_joe.const import (
    active_errors,
    binary_sensor_keys,
    error_text,
    model_name,
    probe_numbers,
    sensor_keys,
    probe_present,
    target_reached,
)
from custom_components.kamado_joe.history import series_from_snapshots
from custom_components.kamado_joe.button import KamadoJoeRefreshButton
from custom_components.kamado_joe.sensor import PROBE_SENSORS, SENSORS

FIXTURES = Path(__file__).parent / "fixtures"


def _off_state() -> dict:
    return json.loads((FIXTURES / "konnected_joe_off.json").read_text())


def test_observed_konnected_joe_off_state() -> None:
    """The observed off payload maps without inventing unavailable values."""
    state = _off_state()

    assert model_name(state["model"]) == "Konnected Joe (C:G:018:1:D)"
    assert probe_numbers(state["model"]) == (1, 2, 3)
    assert "grill_temp" in sensor_keys(state["model"])
    assert "heat_intensity" in sensor_keys(state["model"])
    assert "high_temperature_alert" in binary_sensor_keys(state["model"])
    assert "low_temperature_alert" in binary_sensor_keys(state["model"])
    assert "door_open" not in binary_sensor_keys(state["model"])
    assert "lid_open" not in binary_sensor_keys(state["model"])
    assert "engaged" not in binary_sensor_keys(state["model"])
    assert active_errors(state) == []
    assert error_text(state) == "OK"
    assert not probe_present(state, 1)
    assert not target_reached(state)


def test_catalog_only_profiles_are_explicitly_model_gated() -> None:
    """Untested catalog models get plausible profiles without a support claim."""
    common = {"grill_temp", "target_temp", "heat_intensity", "rssi", "error"}
    binary = {
        "power",
        "heating",
        "problem",
        "target_reached",
        "high_temperature_alert",
        "low_temperature_alert",
    }

    assert probe_numbers("C:G:024:1:D") == (1, 2, 3)
    assert probe_numbers("P:G:018:1:D") == (1, 2)
    assert common <= sensor_keys("C:G:024:1:D")
    assert common <= sensor_keys("P:G:018:1:D")
    assert binary <= binary_sensor_keys("C:G:024:1:D")
    assert binary <= binary_sensor_keys("P:G:018:1:D")
    assert probe_numbers("unknown") == ()


def test_history_extracts_kamado_shadow_shape() -> None:
    state = _off_state()
    state["mainTemp"] = 225
    state["heat"]["t2"]["trgt"] = 250

    series, unit = series_from_snapshots(
        [{"timestamp": 110, "shadow": state}], start=100
    )

    assert unit == "°F"
    assert series["grill"] == [[10, 225.0]]
    assert series["target"] == [[10, 250.0]]


def test_temperatures_are_unknown_while_controller_is_off() -> None:
    """Retained readings must not look current after a logical shutdown."""
    state = _off_state()
    state["mainTemp"] = 86
    state["probes"]["p1"] = {"temp": 93}

    grill = next(desc for desc in SENSORS if desc.key == "grill_temp")
    probe = next(desc for desc in PROBE_SENSORS if desc.key == "probe1_temp")

    assert grill.value_fn(state) is None
    assert probe.value_fn(state) is None


def test_refresh_button_is_not_diagnostic() -> None:
    """Manual refresh belongs with controls, not diagnostic entities."""
    assert "_attr_entity_category" not in KamadoJoeRefreshButton.__dict__
