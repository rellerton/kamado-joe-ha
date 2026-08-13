# Project status

Paused on 2026-08-13 pending the next real cook.

## Current state

- `v0.1.0` is installed and running successfully in production Home Assistant.
- `v0.1.1` is the current GitHub release. It contains documentation and HACS
  installation-page formatting improvements; runtime integration code is
  unchanged from `v0.1.0`.
- The tested hardware is a Konnected Joe running firmware `02.00.30`.
- Production setup completed successfully and created the expected entities.
- Production logs showed no integration setup or runtime errors at this
  checkpoint. Home Assistant's normal warning for an unreviewed custom
  integration is expected.
- Basic powered-on/off telemetry, targets, probes, fan speed, adaptive polling,
  stale-state handling, manual refresh, and the Home Assistant dashboard card
  have been exercised without an identified blocking issue.
- The local Home Assistant lab is intentionally stopped with its configuration
  preserved. Its container is `home-assistant-lab`; the Aiper lab is separate
  and must not be stopped or modified as part of Kamado Joe work.

## Next real-cook validation

- Validate grill temperature and target behavior throughout ignition, warm-up,
  cooking, shutdown, and cooldown.
- Validate the grill **At target temperature** binary sensor against physical
  behavior. Probe equivalents remain structurally supported but are not a
  maintainer-tested feature.
- Confirm fan-speed behavior during a real fire and retained cook-history data.
- Review polling transitions between active, logically off, and stale modes.
- Capture and fix any Konnected Joe-specific problems before declaring the
  integration stable.

## Promotion plan

After successful real-cook validation:

1. Resolve observed model-specific issues and add regression tests.
2. Review documentation and diagnostics against the validated behavior.
3. Promote the integration to a stable `v1.0.0` release.
4. Complete the submission work for inclusion in the default HACS repository.

HACS may retain custom-repository metadata for approximately 48 hours. Use its
**Update information** action when a newly published release or README must be
discovered immediately.
