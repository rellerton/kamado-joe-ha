# Protocol observations

This document records sanitized interoperability findings. It intentionally
omits user identifiers, device addresses, tokens, private keys, and raw payloads.

## Android application

- Package: `app.kamadojoe`
- Observed release: `1.0.31-kamadojoe`
- Application namespace: `com.mb`
- Build flavor: `kamadojoe`
- CAS base: `https://cas.kamadojoe.com/`
- Product catalog base: `https://product.api.middlebyoutdoor.com/`

The application contains REST clients for authentication, paired devices,
current shadows, cook sessions, product families, and product definitions. It
also contains AWS IoT, Cognito, certificate-provisioning, MQTT shadow, BLE scan,
and BLE provisioning code.

## Confirmed read routes

- `POST /api/v1/auth/login` — account authentication only
- `POST /api/v1/auth/refresh`
- `GET /api/v1/paired-device`
- `GET /api/v1/paired-device/{paired_mac}/shadows/current?thing_name=...`
- `GET /api/v1/paired-device/{device_mac}/sessions`
- `GET /api/v1/paired-device/{device_mac}/sessions/last`
- `GET /api/v1/paired-device/{device_mac}/sessions/{id}`
- `GET /brands/kamadojoe/products`
- `GET /brands/kamadojoe/families`

The paired-device identifier includes a two-byte prefix. Session routes use the
remaining device address. The AWS thing name uses the same salted-MD5 derivation
as the related Masterbuilt application.

## Konnected Joe observation

The tested device identifies as model `C:G:018:1:D`, MCU `3`, configuration `5`.
An off-state shadow on firmware `02.00.30` contained:

- model and firmware version
- power and Fahrenheit flags
- lid and door flags
- heating channels
- notifications and accessory state
- error slots
- Wi-Fi signal
- engaged state
- optional probes

The shadow's metadata contains per-leaf timestamps. Freshness must use those
reported timestamps rather than assuming the response time means the appliance
recently communicated.

## Recorded cook evidence

The account retained 32 completed cook sessions. The newest session contained
8,633 snapshots spanning roughly 26 hours. Across that real cook:

- `pwrOn` remained true.
- `mainTemp` ranged from 85 °F to 389 °F.
- `heat.t2.trgt` changed among targets from 225 °F to 415 °F.
- `heat.t2.heating` changed between false and true.
- `heat.t2.intensity` ranged from 0 to 100.
- The product catalog enables `sessionGraph.fanSpeed`, and intensity was always
  zero when `heat.t2.heating` was false. The integration therefore presents
  `heat.t2.intensity` as fan speed for this model.
- `notifications.high_temp` and `notifications.low_temp` both changed during
  the cook while the error list remained empty, so they are exposed as distinct
  temperature-alert binary sensors.
- `accs.mode` remained `0` throughout the observed cook; no user-facing mode is
  exposed until additional values and their meanings are observed.
- `RSSI` changed between -74 dBm and -51 dBm.
- `lidOpn` changed, but the owner confirms the official app does not expose a
  lid or door sensor; it is therefore not promoted as a supported HA entity.
- `doorOpn` and `engaged` never changed and are likewise not exposed.
- No meat probes were connected during the captured cook, so probe parsing is
  based on the known three physical ports and still needs a connected-probe
  observation.

A later powered-on, deliberately unignited test reported `heat.t2.heating=true`
and `heat.t2.intensity=100` after a grill target was set. The integration labels
this as temperature-control demand rather than proof of combustion. That test
also confirmed live `probes.p1` and `probes.p2` temperature and target fields.
No timer field appeared in the active reported shadow.

This evidence supports current temperature, target temperature, heating,
heating intensity, power, errors, Wi-Fi signal, and three optional meat probes.
Heating intensity is diagnostic and disabled by default because the official
app does not present it as a normal control or status value.

## Write boundary

The Android app contains a separate AWS IoT write path using temporary AWS
credentials and a per-install certificate. Masterbuilt's public integration
demonstrates a similar mechanism, but its Cognito and policy-attachment values
must not be assumed valid for Kamado Joe. Writes remain disabled until the
Kamado-specific contract is captured and verified.
