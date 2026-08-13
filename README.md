# Kamado Joe for Home Assistant

An experimental, unofficial Home Assistant custom integration for connected
Kamado Joe grills. It reads live grill telemetry and retained cook history from
Kamado Joe's cloud.

> [!WARNING]
> This project is under active development, is not affiliated with or endorsed
> by Kamado Joe or Middleby, and is not ready for production use. It depends on
> undocumented cloud interfaces that Kamado Joe may change or remove at any
> time. Never use Home Assistant telemetry as the sole indication that a
> live-fire appliance is safe, cool, or powered off.

## Model status

| Product | Cloud model | Profile | Probe slots | Evidence |
|---|---|---|---:|---|
| Konnected Joe | `C:G:018:1:D` | Tested | 3 | Physical grill, current shadow, and 32 retained cooks; firmware `02.00.30` |
| Big Konnected Joe | `C:G:024:1:D` | Experimental, untested | 3 | Kamado Joe catalog and product documentation only |
| Pellet Joe | `P:G:018:1:D` | Experimental, untested | 2 | Kamado Joe catalog and product documentation only |

The two untested profiles make conservative assumptions from their shared
Kamado Joe cloud catalog: grill and target temperature, power, heating, fan
speed, high/low temperature alerts, errors, signal strength, cook history, and
the documented number of meat-probe ports. They may be incomplete or wrong.
Please do not report either model as supported until a real payload has been
captured and its entities verified.

Unknown model codes receive only minimal error and signal diagnostics rather
than inheriting another grill's capabilities.

## Current features

- Kamado Joe account authentication and Home Assistant reauthentication
- Paired-grill discovery and selection
- Current AWS Device Shadow state through the Kamado Joe CAS API
- Grill temperature and target-temperature sensors
- Power, temperature-control demand, at-target-temperature, and high/low alert binary
  sensors
- Fan-speed output and Wi-Fi signal diagnostics
- Up to three model-gated meat-probe temperatures and targets
- Device-report timestamp, data age, and stale-data warning
- Adaptive polling: 30 seconds while fresh and ten minutes after prolonged
  staleness
- A manual **Refresh data** button for immediate power-on discovery
- Current and previous cook metadata
- Read-only actions for listing and retrieving retained cook history
- Privacy-filtered Home Assistant diagnostics

The target entities are currently sensors, not controls. The integration does
not yet write settings to the grill.

## Deliberate limitations

Not implemented:

- Grill or probe target-temperature changes
- Cook timers
- Accessory-mode changes
- Power on/off or automatic ignition
- Direct AWS IoT/MQTT control
- Local Bluetooth control

The official app uses a separate AWS IoT certificate and MQTT path for writes.
No write will be implemented from a guessed or borrowed payload. Power and the
Automatic Fire Starter remain physical-only unless Kamado Joe documents and
exposes a safe remote contract.

## Installation

This integration is currently distributed as an experimental HACS custom
repository. It has been exercised with Home Assistant 2026.8.1, but only the
Konnected Joe profile has been tested on physical hardware.

1. In HACS, open **Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/rellerton/kamado-joe-ha` and select **Integration**.
4. Find **Kamado Joe (Unofficial)** in HACS and install it.
5. Restart Home Assistant when HACS requests it.
6. Go to **Settings > Devices & services > Add integration**, search for
   **Kamado Joe (Unofficial)**, and authenticate with the Kamado Joe account
   that owns the grill.

HACS installs only `custom_components/kamado_joe`; repository documentation,
tests, and development files are not copied into Home Assistant. Because the
cloud interface is undocumented, review release notes before upgrading.

## Diagnostics and data freshness

The integration initially polls every 30 seconds. A logical app shutdown is not
proof that the grill's physical power switch is off, so it retains that cadence
for a 30-minute grace period. Polling then backs off to once every ten minutes
when every selected grill has either remained logically off or produced no new
device-generated report for the full grace period. It stays backed off until a
poll—or the manual **Refresh data** button—finds a fresh `pwrOn=true` state.
Both intervals and the grace/staleness threshold are configurable.

The logical-off timer is intentionally local. Restarting Home Assistant while a
controller is already off restarts its 30-minute grace period; this favors a
small number of extra reads over delaying detection due to an uncertain retained
timestamp.

Automatic active-cook discovery can therefore take up to the stale polling
interval after a long-off period. Press **Refresh data** immediately after
physically powering on when that delay is undesirable.

- **Last reported** is the newest device-generated timestamp in the AWS shadow.
- **Data age** is the number of seconds since that timestamp. It is a detailed
  diagnostic and is disabled by default.
- **Stale data** becomes active after 30 minutes by default. A stale cloud
  shadow can say that a grill is off even if its Wi-Fi controller merely
  stopped reporting, so safety-related notifications should check this sensor.
- **Fan speed** is `heat.t2.intensity`. On the tested Konnected Joe it contained
  83 distinct values from 0–100% across a retained cook and was always 0% when
  heating was inactive. The Kamado Joe catalog also enables fan-speed history.
- **Temperature control active** is the raw `heat.t2.heating` flag. A live test
  showed it active with the fan at 100% after a target was set even though the
  charcoal had not been ignited. It indicates controller demand, not confirmed
  combustion, flame, or physical heating.

### At-target-temperature sensors

**At target temperature** and the per-probe **At target temperature** entities are derived
locally by comparing the current reading with its target using a 5°F/3°C
tolerance. The cloud does not report an explicit “target reached” state.

- The grill calculation still needs validation during a real, ignited cook.
- The probe calculations are structurally identical but are not actively
  validated by the current maintainer, who uses separate wireless probes. They
  will remain available unless real-device feedback identifies a problem.

Polling and staleness thresholds are configurable in the integration options.

Grill and probe temperatures are intentionally shown as unknown while the grill
reports power off. The cloud can retain plausible-looking readings after
shutdown, but those values have not been established as current or meaningful.

## Cook history

Home Assistant Recorder naturally builds temperature, target, fan-speed,
heating, and alert history from the time the integration is installed. The
cloud-history actions can list earlier cooks or retrieve one bounded,
downsampled series without importing thousands of historical samples into the
Recorder database. See [`docs/dashboard.md`](docs/dashboard.md).

## Security and privacy

- Account credentials stay in the Home Assistant config entry and are sent
  only to Kamado Joe's authentication service.
- Access tokens remain in memory.
- Diagnostics redact credentials, account/device identifiers, network names,
  and raw shadows that could reveal them.
- Raw APKs, reverse-engineering captures, certificates, and credentials are not
  part of this repository.

## Project origin and credits

This is intended to be a standalone Kamado Joe project, not a continuing fork
of a Masterbuilt integration. Its initial structure was derived from
[`lucvan/masterbuilt-gravity-ha`](https://github.com/lucvan/masterbuilt-gravity-ha),
which builds on Martin Hruška's original integration and CAS reverse-engineering
work. Luc Van's onboarding, reauthentication, staleness, and cook-history work
also provided the starting architecture. Their MIT copyright notices and
license are retained in [`LICENSE`](LICENSE).

Kamado Joe-specific endpoints, model profiles, payload mappings, and tests were
derived independently from the public Kamado Joe Android application, the
Kamado Joe product catalog, public product documentation, and personally owned
hardware.

The included icon is an original generic ceramic-grill illustration. It does
not reproduce the Kamado Joe logo or wordmark. “Kamado Joe,” “Konnected Joe,”
“Big Joe,” and “Pellet Joe” are used only to identify compatible products and
remain the property of their respective owner.

## License

MIT. See [`LICENSE`](LICENSE). The software is provided without warranty.
