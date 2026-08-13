# Changelog

## 0.1.1 - 2026-08-13

- Improved README formatting for the HACS interface.
- Added prominent HACS and manual installation instructions.
- Added the integration icon to the README.

## 0.1.0 - 2026-08-13

- Established the standalone `kamado_joe` integration domain and Kamado Joe
  cloud authentication endpoints.
- Added a tested capability profile for Konnected Joe model `C:G:018:1:D`.
- Added explicitly untested catalog profiles for Big Konnected Joe and Pellet
  Joe.
- Added live telemetry, fan speed, temperature alerts, model-gated probes,
  report freshness, cook metadata, cook-history actions, and redacted
  diagnostics.
- Added adaptive fresh/stale polling, an immediate manual refresh button, and
  off-state masking for retained grill and probe temperatures.
- Kept all appliance writes disabled pending verification of the Kamado Joe
  AWS IoT control contract.
