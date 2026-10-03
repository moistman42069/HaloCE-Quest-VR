> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Quest test10 — continuation and delivery checkpoint

Updated 2026-10-02. Active checkout: `<workspace>`. Historical remote:
`https://github.com/moistman42069/HaloCE-Quest-VR`; branch `quest-vr-test9-wip`
(name retained for continuity). Build/cache/package work stays on D:.
This is Halo CE native Quest, not the separate Halo-MCC-VR workspace.

## User evidence / accepted results

Test9 source `224a73df3a061473c3d273cb5c1cdf4b36a8718d`: the user reports a
better build, working multiplayer and good fingers. This is direct headset
evidence for those features, not acceptance of every feature. The stable
`quest-vr` test8 branch remains untouched. Test10 requires a new headset result.

Reviewed both supplied recordings; originals remain in the user's Downloads:

- `com.oculus.vrshell-20261002-230006-0.mp4`, 61.221s: launcher listing seven
  servers / eighteen reported players, System Link, then multiplayer play.
- `com.oculus.vrshell-20261002-230124-0.mp4`, 273.945s: hand/tree contact around
  112–148s; settings around 195–260s; close enemy contact and intrusive body
  geometry around 260–270s. Frames do not prove exact input, latency or FPS.
- Extracted contact sheets: `<private-work>\test10\video`, local evidence
  excluded from the source archive.

## Every new request

Implemented means source/build work; headset behavior still needs testing.

| Request | Candidate behavior and limits |
| --- | --- |
| More multiplayer servers | Reads the full verified Chupathingy feed; capacity raised 128 to 512. Merges up to four HTTPS TSV/JSON directories, deduplicates invites, retains other sources if one fails. No second verified compatible public service found. No invented servers or population. |
| Most populated first | Global descending reported players after merging; ties use compatible/open first, then name. Directory above saved invites. Full/incompatible entries marked and cannot be joined. Counts are host reports. |
| Detailed log every launch in Downloads | RunLog creates an immediately visible timestamped MediaStore row in Download/HaloCE before native startup. JNI supplies duplicate append descriptor to native logging. Launcher, device/Android/ABI/memory, activity lifecycle, directory results, joins, Java exceptions and native diagnostics share the log. Latest ten app-owned logs retained. Private fallback path shown if Downloads fails; native private mirror retained. Device confirmation needed. |
| Performance details | Existing 300-frame timing summaries default on for new/default configurations, without GPU stalls. Explicit existing vr.timing=false respected; enable in config for timing. Native runtime/headset, settings, melee/weapon and crash diagnostics retained. |
| Lower settings | Left half of a VR setting row selects previous; right half selects next. Navigation/category buttons unchanged. Stick left/right supported; numeric endpoints still clamp. |
| Support weapon until first grip | Removes automatic loose-gun timeout/drop. Spawn/pickup/switch weapons stay supported in HAND_LOOSE until deliberate grip. Releasing a held weapon still drops, holsters or transfers it. |
| Backward movement while gripping | Arm-run never overwrites deliberate stick input. Contributes only with both axes near neutral, aiming and on foot. Residual push resets outside play, seated or without both tracked hands. |
| Hand contact responsiveness | Seven bounded head-to-palm probes sample a 2.5cm palm radius; single wrist ray could miss grazing surfaces. Immediate correction, accepted finger posing preserved. Still an approximation, not rigid-body hand physics. |
| Physical melee accuracy | Seven 3.5cm-offset sweeps, earliest contact, eye-to-start occlusion checks. Empty hands lose the erroneous weapon's extra 20cm contact offset. Authored unarmed damage when available, carried-weapon damage fallback otherwise. Tracking jumps over 1m/tick rejected; cooldown resets on invalid gameplay/unit state. Multiplayer authority restrictions retained. |
| Closer contact without noclip | vr.close_contact / VR page CLOSE CONTACT reduces offline local VR capsule radius 15%, capped at 5cm, minimum 18cm (never enlarges stock radius). Height/feet unchanged; all bipeds.c radius consumers use the same calculation. Solid collisions remain; network colliders stock. Toggle off for comparison. Needs stairs/doors/crouch/enemy device checks. |
| Body refinements | Render-copy bones follow the same locomotion heading as IK shoulders instead of independent gun aim. First-person local body suppressed while dead/seated to avoid intrusion. Existing arm IK and animated legs retained. |
| Titanfall-style IK | CircuitLord advertises full-body IK but its mod is closed source. Independent upper-body alignment refined; no new full-body/foot-placement IK claimed. Leg/hip tracking and avatar calibration remain open, requiring headset measurements. |
| VR campaign co-op host/browser/join | Investigated, still open. Existing transport and authoritative AI/object replication are useful foundations; local campaign setup and unsynchronized script/checkpoint/transition lifecycle are not working online campaign. See COOP-FEASIBILITY.md for evidence and implementation phases. No fake host/join controls. |
| Other video issues | Enemy activity while settings are open is visible; cause not established. Pages inherit stock pause screen, so no speculative global pause override. Compare stock pause and capture log. Intrusive body near death addressed above. |

Earlier standing requirements remain in TEST9-PROGRESS.md and QUEST_VR_HANDOFF.md:
immersive cutscenes, scope/vehicles, graphics presets, Quest 1/2 performance,
SPV1 and physical reload. No new acceptance inferred. Reload remains deferred.

## Build and handoff

- Commands: `bash tools/build-quest.sh vr`, preserve APK, then
  `bash tools/build-quest.sh flat`. Shared native staging changes between modes.
- VR and flat builds succeeded (exit 0), with APKs preserved separately.
  Existing clang visibility/macro and Android deprecated-API warnings remain;
  no build errors. Local build logs are in <private-work>\test10.
- No headset attached, APK installed or game launched. No new automated
  gameplay/unit-test suite run in this refinement pass.
- `tools/package-quest.py --label test10` checks signature/package/ABI,
  browser/log classes, native identity, OpenXR separation, ZIP integrity and
  clean committed source. Source archive is git archive of the manifest commit.
- Delivery: `<artifacts>\test10-20261002`; manifest.json records source
  commit, hashes and signing certificate. No maps or signing keys included.
- Push only private WIP. No stable merge, installation or public publication.
  Wait for the user's headset result after delivery.

## Next device report

1. Confirm fresh Download/HaloCE/halo_log_*.txt after launching and quitting;
   send it with the next video, including any crash report.
2. Lower/raise settings and confirm persistence.
3. Load without grip, then grip/release; holster, pickup, transfer; backward
   and diagonal movement while gripping/swinging arms.
4. Palm contact, melee, torso yaw, crouch, stairs, doors, death/respawn;
   compare CLOSE CONTACT off for stock capsule.
5. Rejoin known multiplayer host; confirm descending population and refresh.
   Test10 does not provide campaign co-op sessions.

## Primary references

- [Android MediaStore](https://developer.android.com/training/data-storage/shared/media)
- [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce)
- [CircuitLord mod description](https://github.com/CircuitLord/CircuitLordVRModInstaller)
