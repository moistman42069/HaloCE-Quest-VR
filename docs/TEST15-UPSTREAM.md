# Test15 upstream integration and version management

## Pinned sources

- `bnunu/halo-ce-universal` at `c3e55ba8131140838a294eb9fd38f73481d10f4b`: native v10 scoreboard ping message.
- `cybersecurity/halo-ce-universal` at `23b542601f2ca505c7a0143703e92fbda6075e18`: native v11 adds 28-byte match options; custom loadouts, time limits, friendly-fire modes, vehicle selection/respawn, team balance, radar filters, unarmed melee and expanded-session infinite grenades.
- Geometry reference: Andiweli/HaloCE-Android-AAOS `a88f25763b8a51335554ef02e613127ee92677d4`.

These are selected integrations into the accepted VR/co-op fork, not a wholesale replacement with the latest upstream menu or engine. Existing Custom Edition safety/placement guards are retained. VR render/interactions/body defaults remain. Upstream continues developing; future commits require review.

## Native protocol handling

PvP hosts advertise **11**, clients accept distributed hosts **9-11**. The canonical settings record is 13,120 bytes. Version 9/10 records are 13,092 bytes; the receiver assembles the complete bounded record, moves its four-byte local-data tail and supplies default extended options. Version 11 carries the 28-byte option block at offset 13,088. Every fragment must have a supported total, nonzero bounded length, consistent total and consecutive offset; malformed match options are rejected before use. Layout assertions remain enabled in the production guest build.

Campaign still advertises **CE01**. Campaign hosts explicitly serialize the old record for both direct joins and lobby broadcasts, preserving accepted test14's wire size. Matching test15 peers are recommended for candidate testing. This does not assert paired backward compatibility until tested on devices. Avatar IDs/protocol and campaign replication remain separate. The v10 ping message uses ID19; campaign IDs32-39 remain reserved as before.

Launcher PvP offers installed map, 14 native variants, name, player cap2-128, score, time, friendly fire, radar, automatic balance, vehicle respawn, unlimited grenades, custom primary/secondary weapons, and private/public listing. The game starts through its normal lobby. Changing the built-in variant there resets extended options to that variant's defaults. Host options are written to the existing configuration with bounds and other sections preserved. Network options expose online play, UPnP, clipboard invites and a fixed tunnel port.

Upstream OpenCE's playtesting-announcements was rechecked through October3 16:37 EDT: organizers reported over100 players and posted an invite image showing128/128. Their event uses rotating `halo://join/` invites and Direct Link; the earlier notice explicitly said no upstream server browser yet. This is evidence of upstream capacity, not a 128-player Quest benchmark. No second verified native directory endpoint was found. ChupathingyCE, configurable catalogs, saved/event invites and LAN discovery remain the supported discovery paths. Private/event-only sessions cannot be enumerated from a public feed.

## Controlled updates

Launcher **Versions & updates** shows installed project/package/protocol and pinned upstream information. An automatic launcher check (default on, six-hour interval, including resume) reads this project's stable GitHub release and upstream's public network header. Check now bypasses the interval. A status panel reports update availability or upstream integration still needed, without blocking play. It never downloads an upstream engine library or unrelated APK over the mod. Both flavor asset names are exact; draft/prerelease, unknown tags, downgrades, unexpected URLs, oversized downloads, missing SHA256 metadata, wrong package, non-newer Android version and wrong signing certificate are rejected.

Downloads permit bounded HTTPS redirects only to GitHub's known asset hosts. A verified complete APK is passed to Android's standard installer after saving the installed APK, active-root config and touch preferences in private `files/update-backup/`. Maps and saves are not modified. Installation requires the user's standard Android approval/source permission. Cancellation stops download/install. No silent uninstall or downgrade occurs; Android rollback may require ADB. Test15 is newer than the accepted public test14 release, so checks correctly offer no downgrade.

Update checks never run from the gameplay activity. The old upstream APK-replacement updater is disabled even if a CI build number exists. Inherited `update.auto` does not enable upstream replacement. Upstream commit history is review evidence; a project's release is the update unit.

## Evidence limits

Automated wire/input/policy tests and successful builds establish code/format behavior. They cannot confirm real NAT traversal, public announce acceptance, frame timing, crowded-server load or mission scripts. No new device installation, launch, online session or update installation was performed by the agent. The candidate is held for the owner's VR/flat, co-op and public PvP tests.

Final upstream review additionally integrated `133d6a5dc1ea65a00ff6369c16d58d167fcd96f7` (free quit PvP player slots and clear unit ownership) and `601a4c1f506662dcd93d79105e3fe69410397a87` (unload a loaded menu map before the next network game). Slot recycling is excluded from campaign spawning. Review cutoff: 601a4c1; later upstream work is not silently included.

### Release metadata contract

The packager generates `compatibility.json` alongside the candidate manifest. Publish that exact file with the accepted APKs when the owner later authorizes a stable release. Do not publish it or candidate binaries during this testing hold. A future stable release without this metadata is reported as needing maintainer review, rather than being silently installed. GitHub's asset digest authenticates the downloaded metadata against release metadata; the APK additionally must match the installed signing certificate.

Schema1 includes project/tag/source, supported native range, campaign protocol, minimum supported installed app code, preserved save/config policies, VR/co-op integration flag, and each package's exact APK filename/SHA256/size/versionCode/minSDK. The updater validates these before download/installation; unknown schema or migration blocks the update. The APK's own package, version, certificate and native payload/VR loader are checked afterward. Maintainers must review and test the integration before declaring these policies and publishing as stable. A protocol integer alone is never treated as permission to install unrelated upstream code.

No silent background APK installation is attempted. Automatic checks provide an in-launcher status; Check now and Download lead to Android's normal installer approval. Checking sends no game files, saves, private logs, invites or configuration. Failure is visible and leaves the current build usable. The updater rejects downgrading this private test15 candidate to public test14.

Backups remain in the app's private `files/update-backup/`: previous.apk, config.toml and touch.json. No data migration is currently performed. For debugging/rollback these debug-signed builds support `adb shell run-as <package>` to retrieve private backups; Android may require an explicit downgrade operation. Never uninstall to downgrade without separately backing up app game data and saves. Automatic uninstall/downgrade is intentionally absent.
