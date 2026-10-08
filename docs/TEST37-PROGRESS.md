# Test37 progress - private candidate

**Target:** 1.0.18-test37 / Android code47 / OpenCE Build157; local host network24.
**Public release:** v1.0.16 / code45 / network23 unchanged. No publication authorized.

## Report and evidence

The owner reports an empty Android server list on mobile data and Wi-Fi and requests actual network switching with population counters, not merely directory filtering. The 11:51 log is from public1.0.16/code45/network23 and predates broker-ready/per-listing diagnostics. It does not identify whether that phone connected to a broker, received incompatible listings or rejected signatures. Do not claim a proven root cause from it.

The live official latest-release API returned Build157 (73dc01d), already integrated by Test36. A catalog snapshot on October8 at19:37UTC reported network24:26 servers/22 open/101 players; network11:10/8/32; network22:1/1/4; network21:1/0/2; network20:1/1/0; network18:1/1/0. These are historical reports, not current population guarantees.

## Implementation scope

- Launcher PvP/co-op directory entry points, deduplicated per-version server/player counts and population-first ordering.
- Startup client target0 (**All compatible**,11-24) or exact11-24, default24. Shared across both browsers and data sets; applied before launch, immutable while the game runs.
- Native discovery and client admission use the chosen target. Hosting remains on network 24, including signed/public advertisement identity. No host downgrade or replacement serializers.
- Original Xbox-map PvP may use11-24. Campaign co-op and Custom Edition require23/24; versions below11 and unknown future versions are unavailable. The ChupathingyCE backward-client model informs this boundary; it is not blanket certification of every old host.
- PvP retains the installed map/game-set chooser. Campaign does not automatically select a matching revision. Preserve full/closed/content/reachability checks and existing invite flow.
- Four MQTT brokers remain mirrors. One public HTTPS catalog is verified, with existing support for up to four compatible custom catalogs. Protocol selection, catalog selection and broker discovery are separate concepts.
- Preserve VR body/scope/turret behavior, mobile controls, Safe geometry, saves, prior artifacts and signing identity. Updater changes are explanatory status only, not arbitrary upstream runtime installation.

The earlier filter-only implementation and the intermediate23/24 host-profile/PC-vehicle-guard plan are superseded. This implementation is backward client acceptance while the local host stays24.

## Validation and open work

Java profile persistence and launcher compilation passed during development. Exact byte comparisons against pinned ChupathingyCE b78e6cfa passed for the core message/header, game-manager header and client/server message-handler files. The focused test_test37_wire.py check passed production advertisement/settings codec and fragment reassembly checks, including ordering and layout rejection. See TEST37-UPSTREAM-INTEGRATION.md for source anchors and limits. Startup caching now uses the existing mutex facility after the guest linker rejected pthread_once. The final full suite and APK builds remain pending; their results must be recorded against the finished source, not inferred from earlier runs. See TEST37-DELIVERY.md when available for actual results, hashes and provenance. No device session or successful historical-network cross-play is claimed here.

Remaining device work includes representative older PvP hosts,23/24 co-op/CE, signed discovery/LAN/direct invites, startup target persistence, controller/touch/VR regression checks and both network types. A launcher listing does not verify NAT, revision, map or password compatibility. Original/Rev1/Rev2 image comparisons are deferred until supplied. Keep unresolved scope/turret/save reports unchanged without exact failure evidence. Do not advance the accepted/public pointer from a clean build alone.

## Final review findings

The production Java directory parser accepted 35 deduplicated live listings on 2026-10-08 20:37 UTC: v11 7 servers/35 reported players; v18 1/0; v20 1/0; v21 1/2; v22 1/4; v24 24/81. This verifies live feed parsing, not server reachability or gameplay.

The full 61-suite run and additional production wire test passed before final lobby-transition hardening. Both APK flavors compiled. Review then confirmed a host accepts clients before choosing its map/mode; an older host can change to campaign after admission. The final source now captures the version at actual join initiation, clears it on reset/disposal, and enforces the old-host campaign/CE restriction on incoming lobby settings before map precache/copy. Unsupported transitions leave through the existing server-rejection cleanup path. The focused capture/reset and transition matrix passed. Both APKs were rebuilt from this final guard. All62 suites now have passing results; see TEST37-DELIVERY.md for the serial-run extractor correction and final APK hashes. The initial admission gate alone was insufficient.
