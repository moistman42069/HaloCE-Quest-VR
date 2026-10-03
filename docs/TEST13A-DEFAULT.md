> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Test13a: Legs + Arms default (2026-10-03)

The user reports Legs + Arms works great and requests only that it become the
default, followed by a new VR APK. The user explicitly permits retaining the
flat APK. This supersedes the previous full-body default and paired packaging
requirement for this update.

Only gameplay setting change: `vr.body` defaults to `legs` instead of `full`.
Saved explicit preferences remain respected; all four body views remain
available. No IK, menu, network, touch or co-op behavior changes. Flat test13
remains the current companion APK, with the same avatar protocol.

VR identity: test13a, version name 1.0-test13a, version code 14. Native identity
and launch log identify the installed build. Use the original signing key.
Build with `bash tools/build-quest.sh vr` on D:, preserve exact APK/source ZIP
and record their hashes after signing/archive checks. Do not install or launch.

This user report confirms satisfaction with Legs + Arms. It does not establish
paired co-op/avatar runtime acceptance or acceptance of unrelated modes.
Earlier evidence and outstanding device checks remain in TEST13-DELIVERY.md.

## Delivery

Packaged under `<artifacts>\test13a-20261003` from source commit
`6c7aabf7c8974ac15e3ab302f94997ab2684dbfd`. This delivery annotation is a later
documentation-only commit; the source ZIP matches the APK revision exactly.

| Artifact | SHA-256 |
| --- | --- |
| HaloCE-Quest-test13a.apk | `b84f21633e3f12cb26f5fde4c02768646f28da452e842895d0a2e59dae5824fa` |
| HaloCE-Quest-test13a-build.zip | `f05c2fab9734b3875515e2e53c9507bab8b6bdddf22321da1eb690d0d029bfe8` |
| HaloCE-Quest-test13a-source.zip | `b85ccdc690361e201ae09ed9c19b85a11bcdc00265a59f487f23ad4a4efacae0` |

`bash tools/build-quest.sh vr` completed with exit 0, including final Gradle
assembly. Logs: `<private-work>\test13a\build-vr.log` and `package.log`.
The scoped packaging script in that scratch directory verified original signing
certificate, version/package/ARM64, native ELF identity, retained menu/body/avatar
markers, OpenXR loader, no maps/keys, clean source and APK/ZIP integrity. Host
ELF hash is identical to test13. No new tests were added or run; no device install
or launch occurred. Flat test13 remains unchanged. Source and this handoff are
pushed to the private `quest-vr-test9-wip` branch; await the user's next request.
