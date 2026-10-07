# Test31 assault-rifle display evidence

Read-only inspection on 2026-10-07; no headset result is implied.

## Inspected asset and method

The locally supplied SPV1 `a10.map` identifies itself as Custom Edition build
`01.00.00.0609`. SHA-256:
`bed789ae9ab7b282ff7fcef83dd524ca2a709796c61e88d37f12b322129cf94d`.
No game asset is included in this repository. Retail Xbox maps were unavailable
in the searched development data locations, so this evidence covers this CE map.

Used `tools/custom_edition_tag_footprints.py::read_cache` for the cache header
and tag data. This protected map repeats `<protected>` names, so its references
were resolved through raw tag-instance IDs, retaining duplicate names instead
of using the helper's name-keyed dictionary. Each reference's full ID and group
were checked before following it.

Layouts were derived from the current 32-bit engine structures:

- `source/objects/object_definitions.h`: `_object_definition`, size `0x17c`.
- `source/items/item_definitions.h`: `_item_definition`, size `0x18c`.
- `source/items/weapon_definitions.h`: `_weapon_definition`, size `0x200`;
  the complete weapon's first-person model reference begins at `0x45c`.
- `source/models/model_definitions.h`: model `0xe8`, node `0x9c`.
- `source/models/models.c`: geometry `0x30`, shader reference `0x20`.
- `port/linux/game/custom_edition_geometry.c`: CE part `0x84`, vertex offset
  field `0x64`; this file verifies the layout and performs local-node remapping.
- `source/rasterizer/rasterizer_model_types.h`: source vertex `0x44`, compressed
  vertex `0x20`. `rasterizer_geometry_compress_vertices` multiplies node indices
  by three and compresses the primary weight to signed 16-bit normalized form.

## Observations

Weapon tag **1242**, label `ar`, references first-person model **1284**. Its
nodes are `frame gun` (0), `frame display` (1), `frame magazine` (2),
`frame ophandle` (3), and `frame safety button` (4).

| Geometry 0 part | Vertices | Active influences | Shader | Current winding helper |
|---|---:|---|---|---|
| 0 | 8 | All display node 1, primary weight 1.0 | `soso` tag 1244; type 4, flags 0 | Covered: below 512 vertices, uniform display parity |
| 1 | 2,705 | Display 1: 26; magazine 2: 924; handle 3: 128; gun 0: 1,627 | `soso` tag 1246; type 4, flags 1 | Falls back: large and mixed parity |
| 3, 5, 6, 7 | 10, 4, 4, 27 | Gun node 0 only | `schi` | Covered by the queued transparent mirror-state correction |

All listed primary weights are exactly 1.0, secondary weights 0.0. Part 0
therefore becomes compressed node byte **3**, weight **32767**, which the
production helper recognizes. Its strip declares 10 triangles including
degenerate strip triangles; part 1 declares 4,244. Neither `soso` shader's flags
enable the engine's two-sided-culling bits.

## Limits and remaining checks

The small display part is covered by the implemented helper. This does not
prove all geometry attached to `frame display` is covered: the 26 such vertices
in part 1 retain the previous fallback. A whole-part cull flip cannot represent
both parities in that part. Any further correction needs triangle-level evidence
and a bounded implementation, preserving original strip winding and shader order.

Verify the retail AR counter and surrounding casing on device in both hands,
with normal and active-camouflage rendering. Also check transparent layers,
weapon switching and frame timing. No visual success or retail-map equivalence
is claimed by this source-level inspection.
