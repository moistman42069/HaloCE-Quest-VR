# Test37 upstream and network audit

## Official release baseline

The live official GitHub latest-release API returned **OpenCE Build157**, tag `build-157`, commit `73dc01d09a21875f14c77b4430f20518d1f5ad09`, published October8,2026 at10:41UTC. Test36 already integrated it. This is the checked baseline, not a claim that upstream cannot change afterward.

- [Build157](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-157)
- [Network24 version bump](https://github.com/OpenCommunityEdition/OpenCE/commit/11117d7c287d519bf263db83273bc26295a87cb9)
- [PR173: PC vehicle set and related changes](https://github.com/OpenCommunityEdition/OpenCE/pull/173)

## Backward client model

The audit pins ChupathingyCE to commit `b78e6cfa00d007592a21b12363b2cbc1b5217997`.
ChupathingyCE advertises its current host protocol while accepting older hosts from11 through24. Its Delta table identifies version11 as a breaking boundary and later versions as additive. This supports investigating backward **client** compatibility; it does not support falsely advertising a current host as an older engine.

- [ChupathingyCE limits](https://github.com/ChupathingyCE/chupathingyce/blob/b78e6cfa00d007592a21b12363b2cbc1b5217997/port/linux/include/halo_port_limits.h)
- [Delta compatibility table](https://github.com/ChupathingyCE/chupathingyce/blob/b78e6cfa00d007592a21b12363b2cbc1b5217997/port/linux/include/delta.h)
- [Client manager](https://github.com/ChupathingyCE/chupathingyce/blob/b78e6cfa00d007592a21b12363b2cbc1b5217997/source/networking/network_client_manager.c)
- [Cross-play harness](https://github.com/ChupathingyCE/chupathingyce/blob/b78e6cfa00d007592a21b12363b2cbc1b5217997/tools/crossplay_test.py)

The cross-play harness covers loopback PvP operations such as spawn/state, kills/damage, scoring, late join/rejoin and vehicles for its selected baselines. It does not prove every historical server version or campaign co-op combination, nor automatically validate this port. Do not consume its signed Delta table under another project's wire identity or describe its tests as tests of these APKs.

Network24 adds the PC vehicle preset in an existing variant byte. An older23 client does not understand that new preset. Accepting an older host with the current client is a different direction from sending current features to an old client. Versions22/23 also involve Custom Edition map naming, checksums and scenario capacity differences. Therefore this candidate retains current host24 and restricts backward11-22 targets to original Xbox-map PvP; campaign/CE require23 or24. Versions below11 and unknown future versions remain unavailable. See the native implementation/tests for final field-level admission checks; this document is not proof of universal wire parity.

## Pinned wire comparison and focused validation

A shallow ChupathingyCE checkout was verified at exactly
`b78e6cfa00d007592a21b12363b2cbc1b5217997`. Byte-for-byte comparisons against this
port passed for `network_messages.h`, `network_messages.c`,
`network_game_manager.h`, `network_client_message_handler.c` and
`network_server_message_handler.c`, all under `source/networking/`. This is
concrete evidence that the audited packet definitions and message handling
match that backward-client reference, not merely a comparison of comments.

Relevant pinned source anchors:

- [Packet definitions](https://github.com/ChupathingyCE/chupathingyce/blob/b78e6cfa00d007592a21b12363b2cbc1b5217997/source/networking/network_messages.c#L263): lines 263-291 define the advertisement/settings codec shapes; advertisement payload is 276 bytes, settings include three shorts, two padding bytes and an 0xE00 data fragment.
- [Settings fragment structure](https://github.com/ChupathingyCE/chupathingyce/blob/b78e6cfa00d007592a21b12363b2cbc1b5217997/source/networking/network_client_message_handler.c#L263): lines 263-271; [reassembly](https://github.com/ChupathingyCE/chupathingyce/blob/b78e6cfa00d007592a21b12363b2cbc1b5217997/source/networking/network_client_message_handler.c#L952) at lines 952-998.
- [Host advertisement](https://github.com/ChupathingyCE/chupathingyce/blob/b78e6cfa00d007592a21b12363b2cbc1b5217997/source/networking/network_server_message_handler.c#L1642): lines 1642-1758, with version assignments at 1714-1715.

The focused `test_test37_wire.py` check passed under WSL using this port's
production codec and verbatim fragment reassembly function. It exercises the
0x114-byte advertisement and four 0xE00 settings fragments reassembled into
0x3340 bytes, including ordering and invalid-layout rejection. This does not
replace real gameplay tests against every historical binary, nor prove
campaign compatibility at versions below the retained 23 floor.

Startup target caching uses the existing mutex facility. The guest linker
rejected `pthread_once`; that unsupported dependency was removed rather than
shipped. Final builds, regression results, package checks and exact hashes are
recorded in TEST37-DELIVERY.md. Admission checks also cover incoming lobby
settings, so an older host cannot bypass the campaign/CE floor by changing
mode after the client joins.

## Test37 behavior

The cached startup client target is0 (All compatible11-24) or exact11-24, default24. The launcher applies it before native initialization and shares it across PvP/co-op/data sets. Native discovery and client admission use it. Hosting remains on network 24 and signatures/listing identity remain truthful. Changing the target requires closing the game; the selector cannot mutate a running session. No older host implementation is loaded and no arbitrary upstream binaries are installed.

The launcher shows reported populations by network, sorted by players, servers, then version; rows retain population ordering. Unsupported returned versions remain visible but cannot be selected. All-compatible totals exclude unsupported protocols and campaign versions below23; directory-wide reports can still show unavailable hosts. PvP joins retain map/game-set selection; campaign does not automatically choose a matching ISO revision.

## Discovery sources

The verified public HTTPS catalog is `https://halo.milenko.org/v1/games.txt`. Its reported network/population data is separate from signed OpenCE MQTT and LAN discovery. Up to four compatible text/schema-1 JSON catalogs can be configured and deduplicated. No second public compatible catalog was verified in this pass. Four existing MQTT brokers (OpenCE, EMQX, HiveMQ and Mosquitto) are discovery mirrors, not four game protocols.

- [Delta API documentation](https://halo.milenko.org/api)
- [Live catalog](https://halo.milenko.org/v1/games.txt)
- [Delta protocol notes](https://halo.milenko.org/delta)

Catalog counts can lag, omit private/LAN games or describe unreachable/full/closed hosts. A failed refresh must be shown as unavailable, not zero. Population is not evidence of compatible game files, NAT reachability or a successful join.

## Validation limits

Preserve public1.0.16 and Test36 artifacts. Final automated results, package signatures/hashes and source provenance belong in TEST37-DELIVERY.md. Device cross-play testing remains necessary, including older original Xbox-map PvP,23/24 campaign/CE, direct invites/LAN/discovery and both APKs. No Original/Rev1/Rev2 image comparison is available yet; the owner will provide files later. No speculative scope/turret/save changes are justified by this networking work.
