---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# core.location_alias

One row per other name a shop goes by. namespace config_key: the shop's short key, the name the other sources and the staff use for it. namespace pbx_extension: a desk extension or a group line that belongs to the shop; a call leg's location_id was resolved through these rows. An extension with no row belongs to no shop (a head-office phone): its calls have no site. One value names one shop. An extension stays aliased after its desk is retired, so old legs still resolve.
