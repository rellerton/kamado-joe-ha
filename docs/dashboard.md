# Dashboard notes

No Kamado Joe-specific dashboard card is bundled yet. During development, add
the integration's entities through Home Assistant's normal entity cards rather
without depending on a brand-specific companion card.

Useful entities include:

- grill temperature and target temperature
- power, heating, high/low temperature alert, and problem binary sensors
- probe temperature and target sensors when a probe is present
- stale data, last reported, and data age diagnostics
- current cook start and last cook

Entity IDs depend on the grill name and the user's entity registry. Automations
and dashboards should target entity IDs selected from the registry rather than
assuming names from this document.
