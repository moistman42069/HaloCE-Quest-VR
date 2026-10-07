# Test34 progress — OpenCE Build 147 and server-row pointer selection

**Status:** source integration and automated checks in progress; private APKs
are not a public release and have no device acceptance yet.

## Target

- Android flat and Quest VR APKs: version **1.0.15**, Android version code
  **44**.
- OpenCE **Build 147 / network 23**, tag commit
  `34e2d4fdd884d503e9e441155404612473591f8e`.
- Preserve the owner-accepted Test31c Android touch/gameplay and Test31b VR
  settings design. Do not publish, push, tag, install, or launch the game.

The direct [OpenCE Build 147 release page](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-147)
marks it Latest. The general release-list metadata has shown Build 145, so the
direct release page and remote tag were cross-checked. This project's public
v1.0.12 remains available and unchanged at OpenCE network 21.

## Completed source work

1. **Server-list pointer:** hovering over a server row now selects it. Other
   list rows retain click selection to avoid accidental activation of nested
   controls.
2. **Network 23:** CE map header checksums are advertised and checked for
   matching maps. All active host setup paths are covered: normal map change,
   campaign transition, playlist setup, and the app's PvP bootstrap. Clients
   compare map name and version before accepting a different map. Stock Xbox
   maps keep version zero.
3. **Build 146/147 CE safety and capacity:** imported and adapted upstream tag
   schemas/validation, corrected CE linear bitmap pitch handling, guarded
   allocation-failure paths, increased widget/light-volume and vehicle-home
   limits, retained the existing client ownership guard for host-owned falling
   bipeds, and bounded co-op enemy growth.
4. **Campaign and camera:** no-spawn Oddball fallback and host-only `bringto`
   are integrated. The Test28 upright follow-camera fix remains; Build 147's
   final axis check now skips only the invalid camera update.
5. **Documentation and launcher guide:** separate the public v1.0.12/network
   21 release from this private network-23 candidate and explain its limits.
6. **VR scope alignment:** the scope layer now shares the calibrated shot
   orientation used to render the zoomed view, while its position and sight
   offset remain tied to the physical aim pose. Its tracking origin uses the
   same 90 cm arm clamp as the rendered hand/weapon view. All scope shapes and
   both hands are covered; pistol/sniper position adjustments now range to
   ±30 cm, including config-loaded values.
7. **Scope report diagnostics:** the supplied 2026-10-07 log identifies the
   older Test30 / 1.0.12 build, not Test34. It shows a held sniper rifle and
   hand aim, but every timing sample reports zero scope-render time and no
   OpenXR layer transition contains `scope`. It records neither an engine zoom
   state nor the effective `vr.scope` value, so it cannot distinguish an
   inactive off-hand trigger from a saved Scope-off setting or a render gate.
   Test34 now logs scope-setting changes, meaningful off-hand trigger states,
   engine zoom transitions, VR pose-gate reasons and scope-window admission,
   only when those states change. Existing ±30 cm alignment behavior remains
   unchanged until a report demonstrates an actual zoomed layer drifting.

Detailed source mapping and limitations: [Test34 upstream integration](TEST34-UPSTREAM-INTEGRATION.md).

## Validation completed

- Focused Build147 validator/network/camera/capacity tests pass.
- Scope regression covers all three scope shapes, left/right hand, calibrated
  shot direction, physical center stability and extended-arm clamping.
- Scope input/gate diagnostics and the explicit right-handed left-trigger
  binding are included in the candidate and player guide.
- Full Quest regression suite passes, including server browser pointer,
  Android touch, VR lifecycle and menu startup.
- CE cache-format suite: 127 passed, 4 skipped because no local CE map files
  are installed; synthetic range and validator fixtures all ran and passed.

## Still required before delivery

- Release-mode native and Gradle builds for VR, then flat Android.
- APK identity/signature/version/package checks and build/source ZIP hashes.
- Record artifacts, hashes, test commands/results, and the owner device-test
  checklist in [Test34 delivery](TEST34-DELIVERY.md).

Host checks cannot verify Quest startup/rendering, actual mobile touch controls,
large CE maps, or live network-23 compatibility. Those remain user device
tests; no “guaranteed” compatibility claim is made.
