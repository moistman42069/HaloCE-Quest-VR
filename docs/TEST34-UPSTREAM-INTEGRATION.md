# Test34 OpenCE Build 147 integration audit

## Upstream identity

This candidate is adapted from the official OpenCE `build-147` tag at commit
[`34e2d4fdd884d503e9e441155404612473591f8e`](https://github.com/OpenCommunityEdition/OpenCE/commit/34e2d4fdd884d503e9e441155404612473591f8e).
The [Build 147 release page](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-147)
marks it Latest and identifies network version 23. The general releases list
has shown stale Build 145 metadata; the direct Build 147 release page and the
repository's `build-147` tag were checked. This project's public v1.0.12 is a
separate, preserved release using OpenCE Build 144/network 21.

This is an Android/Quest adaptation, not a claim that the APK is byte-for-byte
identical to upstream desktop binaries. The game sources and protocol paths
are brought forward where applicable; Android's CE file loader, memory map,
audio conversion, and VR camera retain platform-specific implementations.

## Build 145 → 147 behavior accounted for

- **Network 23 / CE map identity:** CE hosts put the cache-header checksum in
  the existing map version field. Clients compare the advertised map name and
  version and preflight local content before accepting the changed map.
  Stock Xbox maps continue to send version zero. A zero CE checksum is
  OpenCE's sentinel and does not provide a guaranteed identity check. This is
  not Xbox ISO/XISO revision detection or a cryptographic content hash.
- **CE schema validation:** the upstream tag schemas and validator are
  integrated. The adapter supplies the app's combined CE map, audio, bitmap,
  and sound ranges and uses its 34.5 MiB (36 MB) Quest tag-cache ceiling. Selected
  scenario vehicle-placement and animation/seat blocks can exceed Xbox tool
  limits while still being checked against runtime bounds, signed indices,
  byte ranges, and overlap. The CE map file-data range is limited to its
  declared `file_length`; physical trailing bytes are not treated as valid
  tag data. Invalid pointer/extent data refuses that cache before gameplay.
  The validator's fixed claims bitmap adds about 4.31 MiB of guest static
  storage and is cleared when a CE tag cache is validated; Quest map-load
  memory and timing should be observed during owner testing.
- **BSP schemas:** the upstream structure-BSP validator runs after the port's
  file/header/range preflight and before GPU buffer registration or CE geometry
  conversion, with the corresponding tag-validation context active.
- **CE bitmap pitch:** linear bitmap rows are padded to the renderer's
  alignment when the resulting pitch fits the device format's field.
- **Capacity:** widget and light-volume pool limits are 2048; vehicle home
  snapshots are 1024.
- **Co-op safeguards:** per-player enemy growth is capped at 8× the authored
  squad size, invalid host-follow camera axes skip only that camera update,
  and a host-only `bringto` command can gather players to the host.
- **Map/gameplay safety:** Oddball falls back to the first player start or the
  origin when a map has no ball spawn. The app already had the matching
  network-ownership guard for client-side deletion of host-owned falling
  bipeds; that implementation is retained.
- **Allocation failure:** the app's CE cache and geometry paths guard game
  allocator frees, and its CE audio transcoder uses the platform audio-free
  routine. The desktop-only upstream CE sound helper is not part of this
  Android/Quest loader architecture.
- **Server-list pointer:** hover focuses a server row, whose row has no nested
  action buttons. Other list types with child controls keep click-to-select so
  pointer travel does not activate a nested action accidentally.

## Compatibility boundaries

All peers must use network 23 for this candidate. Network 21 and 22 peers
cannot join it. Build 147's CE checksum is a map-header check; it does not
identify every Xbox disc revision, modified ISO/XISO, or extracted game set.
Stock-map compatibility continues to depend on the content and engine paths
that the network protocol does not checksum. A server listing also cannot
guarantee reachability through NAT, mobile networks, or a failed host.

The schemas validate the structures this port reads and the ranges represented
by this cache integration. They do not add OpenSauce's absent runtime systems,
prove compatibility with every CE map, or certify every ISO/XISO revision.

## Verification record

Automated source/host checks are recorded in
[`TEST34-DELIVERY.md`](TEST34-DELIVERY.md). Passing those checks does not
replace loading representative maps, joining network-23 sessions, or the
owner's Quest and phone testing. Do not call this candidate device-accepted
until those results arrive.
