# Development rules

This repository targets a live-fire appliance. Safety constraints override
convenience and feature parity.

## Source and secret handling

- Never commit account credentials, bearer/refresh tokens, AWS temporary
  credentials, X.509 private keys, device MAC addresses, Wi-Fi SSIDs, raw APKs,
  or unsanitized API/shadow/session captures.
- Keep reverse-engineering captures outside the repository and restrict them to
  the current Windows user.
- Public application constants recovered from a release APK may be documented
  in code only when required for interoperability and clearly identified as
  app-level—not user—credentials.
- Preserve upstream license, copyright, and attribution.
- Treat this as a standalone Kamado Joe project. Do not restore inherited
  Masterbuilt domains, branding, entity profiles, release tags, or installation
  instructions.

## Appliance safety

- Read-only API and shadow inspection is permitted during investigation.
- Do not publish AWS IoT/MQTT messages, change targets or timers, or control the
  grill without an explicit user request for that exact action.
- Never implement or test power on/off using a guessed, borrowed, or partially
  understood payload.
- Never use a wildcard MQTT publish.
- Treat stale cloud data as untrustworthy; do not infer that the physical grill
  is safe or off solely from an old shadow.

## Implementation discipline

- Keep Kamado Joe endpoints, models, and capability decisions separate from
  Masterbuilt assumptions even where the apps currently share code.
- Gate model-specific behavior by the raw cloud model code.
- Do not claim support for a model that has only appeared in the product catalog.
- Add sanitized fixtures and tests for every new payload mapping.
- Validate against an isolated Home Assistant instance before proposing a
  production installation.
- Investigation is not authorization to make a consequential appliance change.
