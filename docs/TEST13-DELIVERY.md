> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Test13 candidate delivery record

Packaged 2026-10-03 on D:. Both APKs and matching build/source ZIPs are from
source commit `68aebbc07f9731f6341a599a7b991f9233a16ac2` on the private
`quest-vr-test9-wip` branch. This delivery-record commit changes documentation
only. Stable `quest-vr` remains the test8 baseline; no headset acceptance is
inferred from compilation or packaging.

Directory: `<artifacts>\test13-20261003`.

| Artifact | SHA-256 |
| --- | --- |
| HaloCE-Quest-test13.apk | `1003d1f7896453cf30d6eac4b14651beedbad225262ab1269dc62b31ff699d9b` |
| HaloCE-Android-test13.apk | `20f5d59eddb64a6088b1304199bf6ba6026523032151235f166f0bdaf4a2894a` |
| HaloCE-Quest-test13-build.zip | `93d5dd07b318cd4a7a70327c7fb004ea4f7ce952f2f9413cd80a66b4e6fe7b63` |
| HaloCE-Quest-test13-source.zip | `f6920a185a5ccae41c55ae77b175670f1070006961870336d048943a1b26cbef` |

The manifest records each native host/guest hash and the original signing
certificate. Both APKs report version `1.0-test13`, code 13, ARM64. Package IDs
remain `com.halo.decomp.vr` and `com.halo.decomp`. No maps or signing keys are
included. The source ZIP is a git archive of the exact APK source commit.

## Changes

- Full body defaults on for new/unset configs; explicitly saved choices remain.
  Four local views: full, arms+hands, torso-hidden legs+arms, and hands only.
- Elbow-plane continuity, bounded shoulder reach and arm extension, continuous
  wrist twist, collar-based shoulders, deeper crouch clearance and local duplicate
  shoulder filtering. Existing room-scale foot planting is retained.
- Paged categories/settings with growing storage, reserved navigation/hint space,
  directional custom-value stepping and independent flashlight choice handling.
- Optional negotiated avatar snapshots for supporting co-op/PvP hosts and peers,
  including flat observers. Render-only body/weapon transforms; no hitbox or
  gameplay-input changes. Older hosts/peers keep stock observer animation.
- Prior logging, browser/population sorting, co-op implementation, touch controls,
  grip, finger/contact, crosshair and SPV1 recovery work retained. Physical reload
  remains previously deferred. Detailed bounds: TEST13-README.md and
  NETWORK-VR-AVATARS.md.

## Build and artifact evidence

Commands completed serially with exit 0:

```sh
bash tools/build-quest.sh vr
# Preserve the VR APK before changing native staging to flat.
bash tools/build-quest.sh flat
python3 tools/package-quest.py --label test13 \
  --vr <private-work>/test13/HaloCE-Quest-test13.apk \
  --flat <private-work>/test13/HaloCE-Android-test13.apk \
  --build-tools <home>/Android/Sdk/build-tools/35.0.0 \
  --out <artifacts>/test13-20261003
```

Logs under `<private-work>\test13`: `build-vr.log`, `build-flat.log`,
`package.log`. Earlier native/Java compile records are in TEST13-PROGRESS.md.
Packaging checked the original certificate, IDs/ABI, native ELF payloads,
test13 VR identity, avatar support in both guests, VR body/page markers, flat-only
touch JNI, VR-only OpenXR loader, browser/co-op/logging classes, clean source,
absence of map/key files and integrity of both APKs and build/source archives.
Separate aapt checks confirmed both version names/codes. No gameplay test suite
was added or run; no device installation, game launch or PR occurred.

## Next acceptance evidence

Await the owner's headset/paired-device results. The implementation and builds
do not prove clipping-free movement or working campaign/observer replication.
Keep both devices' Download/HaloCE launch logs and recordings for:

- Menu paging/decrement; all body modes; overhead/cross-body/straight/downward
  arms, wrist rotation, crouching, room-scale steps and support grip alignment.
- Quest-to-Quest and Quest-to-flat co-op; remote head/arms/torso/legs; respawn,
  checkpoint/BSP/restart/next mission, reconnect and packet-loss fallback.
- Supporting PvP host with new and old clients; ordinary public-server play.

Stock biped hands have no individual finger bones. Public directory acceptance
of the campaign protocol remains unverified; use private invites if rejected.
No claim that old public servers relay the new avatar protocol is made.

Claude Cloud/VS Code: read this record, TEST13-PROGRESS.md,
NETWORK-VR-AVATARS.md, CAMPAIGN-PROTOCOL-WIP.md and
CLAUDE-CLOUD-VSCODE-WORKFLOW.md. Preserve this source revision and artifacts
for diagnosis; await device results/instructions before another candidate.
