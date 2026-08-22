# Kamado Joe for Home Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/rellerton/kamado-joe-ha/main/custom_components/kamado_joe/brand/icon%402x.png" alt="Kamado Joe integration icon" width="160">
</p>

An unofficial Home Assistant custom integration for connected Kamado Joe
grills. It reads live grill telemetry and retained cook history from Kamado
Joe's cloud.

> [!WARNING]
> This community-maintained project is not affiliated with or endorsed by
> Kamado Joe or Middleby. It depends on undocumented cloud interfaces that
> Kamado Joe may change or remove at any time. Never use Home Assistant
> telemetry as the sole indication that a live-fire appliance is safe, cool,
> or powered off.

## Installation

### Install with HACS

1. Open **HACS** in Home Assistant.
2. Select **Integrations**.
3. Open the three-dot menu and select **Custom repositories**.
4. Enter `https://github.com/rellerton/kamado-joe-ha`.
5. Select **Integration** as the category, then choose **Add**.
6. Find **Kamado Joe (Unofficial)** and select **Download**.
7. Restart Home Assistant when HACS requests it.
8. Open **Settings > Devices & services**.
9. Select **Add integration** and choose **Kamado Joe (Unofficial)**.
10. Sign in with the Kamado Joe account that owns the grill.

### Manual installation

1. Download the latest release from GitHub.
2. Copy `custom_components/kamado_joe` into the Home Assistant configuration
   directory at `custom_components/kamado_joe`.
3. Restart Home Assistant.
4. Add **Kamado Joe (Unofficial)** from **Settings > Devices & services**.

Review the release notes before upgrading. The integration depends on an
undocumented cloud interface and compatibility can change without notice.

## Supported models

### Konnected Joe

- Cloud model: `C:G:018:1:D`
- Status: **Tested on physical hardware**
- Probe slots: 3
- Evidence: current device shadow, 32 retained cooks, and firmware `02.00.30`

### Big Konnected Joe

- Cloud model: `C:G:024:1:D`
- Status: **Catalog profile; not hardware-validated**
- Assumed probe slots: 3
- Evidence: product catalog and documentation only

### Pellet Joe

- Cloud model: `P:G:018:1:D`
- Status: **Catalog profile; not hardware-validated**
- Assumed probe slots: 2
- Evidence: product catalog and documentation only

The untested profiles make conservative assumptions from their shared
Kamado Joe cloud catalog: grill and target temperature, power, heating, fan
speed, high/low temperature alerts, errors, signal strength, cook history, and
the documented number of meat-probe ports. They may be incomplete or wrong.
Please include diagnostics when reporting results for either model so its
profile can be verified against physical hardware.

Unknown model codes receive only minimal error and signal diagnostics rather
than inheriting another grill's capabilities.

## Current features

- Kamado Joe account authentication and Home Assistant reauthentication
- Paired-grill discovery and selection
- Current AWS Device Shadow state through the Kamado Joe CAS API
- Grill temperature and target-temperature sensors
- Power, temperature-control demand, at-target-temperature, and high/low alert
  binary sensors
- Fan-speed output and Wi-Fi signal diagnostics
- Up to three model-gated meat-probe temperatures and targets
- Device-report timestamp, data age, and stale-data warning
- Adaptive polling: 30 seconds while fresh and ten minutes after prolonged
  staleness
- A manual **Refresh data** button for immediate power-on discovery
- Current and previous cook metadata
- Read-only actions for listing and retrieving retained cook history
- Privacy-filtered Home Assistant diagnostics

The target entities are sensors, not controls. The integration is intentionally
read-only and does not write settings to the grill.

## Deliberate limitations

Not implemented:

- Grill or probe target-temperature changes
- Cook timers
- Accessory-mode changes
- Power on/off or automatic ignition
- Direct AWS IoT/MQTT control
- Local Bluetooth control

Power and the Automatic Fire Starter remain physical-only. This integration
does not send grill-control commands.

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

**At target temperature** and the per-probe **At target temperature** entities
are derived locally by comparing the current reading with its target using a
5°F/3°C tolerance. The cloud does not report an explicit “target reached” state.

- The grill calculation is available on the hardware-validated Konnected Joe
  profile.
- The probe calculations use the same tolerance but have not been independently
  hardware-validated by the current maintainer, who uses separate wireless
  probes.

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

## Project origin and credits

This is intended to be a standalone Kamado Joe project, not a continuing fork
of a Masterbuilt integration. Its initial structure was derived from
[`lucvan/masterbuilt-gravity-ha`](https://github.com/lucvan/masterbuilt-gravity-ha),
which builds on Martin Hruška's original integration. Luc Van's onboarding,
reauthentication, staleness, and cook-history work also provided the starting
architecture. Their MIT copyright notices and license are retained in
[`LICENSE`](LICENSE).

Kamado Joe-specific endpoints, model profiles, payload mappings, and tests were
developed independently for this project and validated with personally owned
hardware.

The included icon is an original generic ceramic-grill illustration. It does
not reproduce the Kamado Joe logo or wordmark. “Kamado Joe,” “Konnected Joe,”
“Big Joe,” and “Pellet Joe” are used only to identify compatible products and
remain the property of their respective owner.

## License

MIT. See [`LICENSE`](LICENSE). The software is provided without warranty.
