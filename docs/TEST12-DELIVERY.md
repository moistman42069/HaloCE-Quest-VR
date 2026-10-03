> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Test12 candidate delivery record

Packaged 2026-10-03 on D:. Both APKs and the matching build/source ZIPs come from
source commit `4fe781ed1571fc098d65b53976bede23be2e1902` on the private
`quest-vr-test9-wip` branch. This delivery-record commit changes documentation
only; it is not the APK source commit. Stable `quest-vr` remains test8.

Directory: `<artifacts>\test12-20261003`.

| Artifact | SHA-256 |
| --- | --- |
| HaloCE-Quest-test12.apk | `c0557561fc1df4ae644fa67a800dc88fc1a4af24a4fa1236c0902d00a4b682b6` |
| HaloCE-Android-test12.apk | `77f9b2c9e63b3c44526ae0def787a036de55222e8d3909b79b3b591d50c3a57a` |
| HaloCE-Quest-test12-build.zip | `a50330bdc516ff665dc6b1ce9bd1a2e7f07a26cf274b0ddd8b6d02aa4a303e6f` |
| HaloCE-Quest-test12-source.zip | `7c09cfde123a9d605c1c94531cccbf1a22d88e3c528032c345745e4b01dc5414` |

The package manifest also records the host/guest ELF hashes, package IDs and
signing certificate. Both packages report `1.0-test12`, version code 12, ARM64.
No game maps, signing key or SDK is included. Source is a git archive of the
exact APK source commit, not an export of a later worktree.

## Build and artifact evidence

Serial commands completed with exit 0:

```sh
bash tools/build-quest.sh vr
# Preserve app-vr-debug.apk before changing the staged native flavor.
bash tools/build-quest.sh flat
python3 tools/package-quest.py --label test12 \
  --vr <private-work>/test12/HaloCE-Quest-test12.apk \
  --flat <private-work>/test12/HaloCE-Android-test12.apk \
  --build-tools <home>/Android/Sdk/build-tools/35.0.0 \
  --out <artifacts>/test12-20261003
```

Logs under `<private-work>\test12`: `build-test12-vr.log`,
`build-test12-flat.log`, `package-test12.log`. Native/Java compile-only checkpoints
are recorded in TEST12-PROGRESS.md. Packaging verified the original signing
certificate, separate IDs/ARM64 ABI, native ELF payloads, test12 VR identity,
flat-only touch JNI, VR-only OpenXR loader, launcher/browser/co-op classes,
absence of map/key files, clean source, and APK/build/source ZIP integrity.

## Remaining acceptance work

No test12 game was launched or installed here. No paired campaign session was
exercised. The host/join, campaign replication and lifecycle implementation is
present; compile/package success does not establish that campaign play works.
Public directory acceptance of campaign version 0xCE01 is also unverified.
Use the private invite if public publication fails, and retain both launch logs.

The next useful evidence is the owner's two-device campaign run: opening
cinematics, AI/weapons/doors, checkpoint and both-dead recovery, BSP change,
restart and next mission. Body/grip/crosshair, flat touch and PvP regression
checks remain pending too. See TEST12-README.md for host/join and scope details.
Do not advance the accepted baseline or claim complete runtime verification.

Claude Cloud/VS Code should read this record, TEST12-PROGRESS.md,
CAMPAIGN-PROTOCOL-WIP.md and CLAUDE-CLOUD-VSCODE-WORKFLOW.md before continuing.
Await the user's device results/instructions; preserve both delivered binaries
and this source commit when diagnosing. Do not install, launch or open a PR.
