# Subsequent VR interaction requirements

## Owner packaging hold — 2026-10-07

Do not package or deliver either APK until **all three task prompts** have been
worked through in full. A passing test31 baseline alone does not clear this
hold. This supersedes the earlier instruction to deliver test31 before starting
these additional workstreams. Keep implementation sequential: baseline fixes
and menus, manual reload/hand contact, then world interaction/NPC handling.
Device acceptance remains pending until the eventual combined candidate is
tested; do not make prior device acceptance a circular prerequisite for doing
the remaining authorized source work. Complete available source/build/test
validation between subsystems instead.

Acknowledging a row or recording an initial dependency does not complete it.
Investigate each dependency and resolve what can be resolved. Any genuinely
unsupported behavior or remaining external dependency requires specific evidence
and an explicit disposition before the packaging decision. No unsupported
feature may be presented as implemented.

Owner requests received after test31 began. **Order: finish and validate test31,
then manual reload/finger architecture investigation and reported plan, then
world-interaction investigation and reported plan.** No new feature here is
implemented or accepted yet. Do not introduce architecture changes before the
required investigation/plan. Work one subsystem at a time; preserve classic
behavior with optional interaction settings OFF by default.

Statuses below are initial dependency deferrals, not final dispositions. Each
row must acquire investigation evidence, implementation/partial/not-viable
decision, automated evidence, and explicit device/network acceptance status
before its workstream can be declared complete. Full request text is retained
in private work records; headings provide stable requirement IDs.

## Manual reload and finger/palm interaction

Dependency M: completed/stable test31, then inspection of reload/ammo authority,
weapon models/nodes/animations, current hands/collision/haptics and interaction
priorities. Report the plan and limits before architecture changes. Start with
AR, expand deliberately. Preserve both left shoulder and left hip grip-only
retrieval, both weapon hands, spatial magazine insertion, ammo conservation,
all interruptions/resets, classic fallback, and standalone performance.

| ID | Requirement | Status | Evidence / next dependency |
|---|---|---|---|
| M1 | Optional manual weapon reloading | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M2 | Physical magazine retrieval | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M3 | Magazine models | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M4 | Magazine removal from the weapon | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M5 | Magazine insertion | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M6 | Weapon state and ammunition synchronization | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M7 | Charging handle / cocking / chambering interactions | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M8 | Weapon-specific interaction definitions | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M9 | Two-handed weapon interaction during reloading | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M10 | Reload cancellation and edge cases | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M11 | Haptic interaction pass | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M12 | Improve finger interaction with world surfaces | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M13 | Per-finger contact behavior | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M14 | Continuous finger solving rather than binary poses | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M15 | Joint-level finger behavior | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M16 | Collision probes | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M17 | Prevent visible penetration | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M18 | Contact smoothing | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M19 | Palm interaction | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M20 | Hand positional compliance | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M21 | Finger contact haptics | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M22 | Interaction with grab poses | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M23 | Interaction with weapons and magazines | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M24 | Left/right hand parity | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M25 | Performance requirements | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M26 | Debugging facilities | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M27 | Automated tests where realistic | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M28 | Device-test checklist | Deferred — dependency M | Investigate; no implementation or device result claimed. |
| M29 | Implementation strategy | Deferred — dependency M | Investigate; no implementation or device result claimed. |

## World interaction, NPCs, ragdolls and impacts

Dependency W: prior assigned work, followed by architecture investigation W59
phase A. Generic props must be verified before two-hand objects or live NPCs;
start NPC work with Grunts, then recovery/AI/damage before expanding classes.
Networking follows stable local behavior. Stock OpenCE wire checks and avatar
messages remain intact. PvP stays disabled unless synchronized fairness and
compatibility are demonstrated. No articulated-ragdoll capability is assumed.

| ID | Requirement | Status | Evidence / next dependency |
|---|---|---|---|
| W1 | VR setting | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W2 | Physical gripping of world objects | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W3 | Grab detection | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W4 | Grabbing from arbitrary points | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W5 | Spartan strength | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W6 | Weight classes | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W7 | Two-handed physical grabbing | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W8 | NPC physical interaction | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W9 | Small enemy grabbing | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W10 | Larger enemy grabbing | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W11 | Friendly NPC interaction | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W12 | Ragdoll system | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W13 | Live ragdoll behavior | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W14 | Dynamic recovery | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W15 | Recovery pose selection | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W16 | AI state restoration | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W17 | Scripted NPC safety | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W18 | Physical throwing | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W19 | Throw trajectory | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W20 | Impact damage | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W21 | Speed-based and mass-based damage | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W22 | Damage caps and tuning | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W23 | Object-as-weapon interaction | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W24 | NPC-to-NPC impacts | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W25 | Ground slams | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W26 | Wall impacts | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W27 | Grab resistance for living NPCs | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W28 | Avoid controller instability | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W29 | Hand pose while grabbing NPCs | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W30 | Grab points on bipeds | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W31 | Constraint stability | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W32 | Object release safety | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W33 | Multiple object interactions | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W34 | Grabbing weapons from the world | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W35 | Grenades and equipment | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W36 | Vehicles and extremely large objects | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W37 | World collision | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W38 | Player-body collision considerations | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W39 | Co-op and multiplayer compatibility | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W40 | Competitive multiplayer | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W41 | Co-op support | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W42 | Mixed-client co-op | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W43 | Port-only enhanced co-op features | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W44 | Authority | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W45 | Damage authority | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W46 | Desync recovery | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W47 | Save/checkpoint behavior | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W48 | Cutscenes | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W49 | Vehicles | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W50 | Player death | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W51 | Teleport/recenter/state reset | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W52 | Performance | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W53 | Physics budgeting | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W54 | Maximum active ragdolls | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W55 | Debug tools | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W56 | Logging | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W57 | Automated testing | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W58 | Device test plan | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W59 | Recommended implementation order | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W60 | Interaction with the previously requested manual reload and finger systems | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W61 | Interaction priority model | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W62 | Haptics | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W63 | Avoid game-breaking behavior | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W64 | Out-of-bounds protection | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W65 | Physical interaction should remain fun | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |
| W66 | Final acceptance requirement | Deferred — dependency W | Investigate after preceding work; no physical/network evidence yet. |

## Evidence required at delivery

Preserve both complete device checklists: M28 (52 checks) and W58 (70 checks).
They cover settings, both-hand interactions, authentic magazine/charging poses,
independent fingers/palm compliance, nonpenetration, throws/mass, NPC species,
recovery/AI/scripts, discrete authoritative impact damage, collision filtering,
checkpoint/death/cutscene/vehicle/tracking cleanup, Quest frame times and mixed
Quest/Android/stock-OpenCE sessions. Compilation is not physical acceptance;
simulations are not multiplayer acceptance. Revisit every row in the final
workstream report, including unsupported entities and explicit dependencies.
