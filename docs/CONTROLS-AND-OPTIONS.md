# Controls and options — test13a VR / test13 flat

These mappings follow the shipped code. Start with Controls = VR and a standard native controller profile. Changing either can change the resulting actions. Touch controllers lack conventional gamepad bumpers/View.

## Quest Touch, default VR layout

| Input | Action |
| --- | --- |
| Left stick | Move/strafe relative to Head, Left Hand or Right Hand setting |
| Right stick | Smooth/snap turn; vertical input can satisfy native look/tutorial prompts |
| Weapon-hand trigger | Fire the held gun |
| Other-hand trigger | Zoom; Scope places the zoomed view at the weapon |
| Right A | Jump / confirm |
| Right B | Reload/use in gameplay; pointer-menu Back in menus |
| Left Y | Switch weapons |
| Left X with Physical weapons active | Tap/release throws; hold 0.4 seconds switches grenade type |
| Left X with Locked weapons | Switch grenade type |
| Weapon-hand grip, Locked | Throw grenade away from holsters; grip at a holster switches weapon |
| Weapon-hand grip, Physical | Hold; releasing after the initial protected grip can drop/holster/transfer |
| Other-hand grip near support region | Lock support hand in Two Hands = Grip; release detaches |
| Left stick click | Crouch |
| Right stick click | Native melee |
| Both stick clicks | Recenter during gameplay; stand normally first |
| Left menu | Pause |
| Weapon pointer + trigger in menus | Select; right B goes back |
| Off hand near head | Flashlight gesture when enabled |

Left-handed mode changes weapon/off-hand trigger roles; Touch face-button sides are not all mirrored. Palms together plus the other hand's grip can transfer handedness. Controllers with bumpers/View use weapon-hand bumper for grenade, off-hand bumper for flashlight, and View tap/hold for Back/recenter. Use the Touch-specific table above on Quest.

Physical weapons is the local default. A gun supplied on load/pickup stays supported until the first grip. Two Hands = Grip requires a squeeze near the support area; simply touching the barrel does not attach. Auto restores proximity attachment; Off disables it. The support point remains fixed until release.

## Gestures

- Crouch compares height against the last recenter; default 35 cm, zero disables physical crouch.
- Flashlight gesture: off hand within 20 cm of the head by default. Button mode disables proximity activation.
- Shoulder/hip holsters: default region size 20 cm, with entry haptics. Locked and Physical modes use them differently as above.
- Arm Run defaults off. Pumping or two-hand weapon bob supplies forward movement with a neutral stick. Lower Run Effort makes activation easier. Strong offline effort can reach 1.5x speed; network speed stays stock. Stick input wins.
- Impact melee sweeps the hand/weapon; Swing requests native melee. Default threshold 2 m/s, zero disables motion melee. The button still works. Network clients use Swing.
- Local finger poses use controller touch/trigger/grip sensors. Free-hand point/thumb/fist and a held gesture are available; this is not optical tracking of individual fingers.
- Full-body IK infers untracked joints. Legs + Arms hides the local chest and retains legs/first-person arms. Supporting peers can still see the full body.

## VR settings

Open the stock campaign pause menu, then **VR Settings**. Screens have four rows per column and reserved navigation space. **Next Page** opens the next screen; Back returns through pages/categories. A/right increases/advances; left decreases. Numeric endpoints clamp; changes save to `config.toml`.

| Category | Menu options |
| --- | --- |
| Controls | VR / Xbox layout; Hand / Head aim; Right / Left gun hand; Smooth / Snap 30 / Snap 45; Turn Speed 45–300 degrees/s; Move With Head / Left Hand / Right Hand; Two Hands Grip / Auto / Off; Weapons Locked / Physical; Holsters Off / On |
| Body | Arms + Hands / Full / Legs + Arms / Hands Only; Arms IK / Hidden / Animated; Fingers Off / Tracked; Room-scale Off / On; Crouch Depth Off or 5–40 cm; Arm Run Off / On; Run Effort 0.2–1.2; Melee Impact / Swing; Melee Speed Off or 1.0–3.6 m/s |
| VR | Haptics 0–100%; Flashlight Gesture / Button; Holster Size 10–40 cm; Scope Off / On; Vehicles Inside / Chase; Steering Stick / Head / Hand; Cutscenes Immersive / 3D Screen / Flat; MP Physical Off / On; Close Contact Off / On |
| Graphics | Preset Auto / Low / Medium / High / Max; Resolution Auto / 70 / 85 / 100 / 115 / 130%; Shadows, Lights, Specular, Reflections, Bump Maps, Grass, Fog Layers: Auto / On / Off |
| Display | Decals, Particles, Contrails, Weather, Lens Flares, Camo: Auto / On / Off; Refresh 72 / 80 / 90 / 120 Hz |
| Crosshair | Native / Off; Size 25–300%; Opacity 0–100% |

Important defaults: body `legs`, arms `ik`; fingers/room-scale/holsters/scope on; hand aim/right gun hand; two-hand Grip; Physical weapons; Arm Run off; MP Physical off; Close Contact on; smooth turn 120 degrees/s; refresh request 72 Hz. Saved values override defaults. Hands Only forces hand IK even if Arms was set to hidden/animated.

Close Contact reduces only the offline local VR capsule radius: up to 15%, at most 5 cm, never below 18 cm. Solid collision and height remain. MP Physical concerns weapon holding/drop behavior, not visual avatar sharing; peers may not reproduce physical drops/pickups correctly.

Auto graphics effects follow the preset. Resolution is relative to runtime eye targets. Refresh requests a supported rate; it does not guarantee frame timing. The simulation remains 30 Hz with interpolated rendering.

## Flat Android touch

| Control | Input / use |
| --- | --- |
| Move | Analog movement/strafe |
| Look | Rate-based analog look: hold away from center to turn, release to stop |
| Fire | Fire; drag while holding also aims |
| A / Jump | Jump / confirm |
| B / Melee | Melee / cancel |
| X / Use | Reload / hold to interact or pick up |
| Y / Swap | Switch weapons |
| Crouch / Zoom | Left/right stick click inputs |
| Grenade | Left trigger |
| Type / Light | Xbox White / Black respectively; actual action follows the native controller profile |
| Menu / Back | Start / Back |
| Arrows | D-pad/navigation |
| Touch | Hide/show overlay; choice saved |

Move + Fire/drag works with two fingers; extra contacts can use other actions. Look is gamepad-rate based rather than relative mouse swipe. Pointer ownership lasts until release and is cleared on pause/focus loss/cancel. Layout positions use fixed screen proportions; no layout editor is included. Phone acceptance, including Type/Light labels against the selected native profile, remains open.

## Flat gamepad and keyboard

SDL receives connected Android gamepads. In a standard Xbox-style profile: sticks move/look; right trigger fires; left trigger throws; A jumps/confirms; B melees/backs; X reloads/uses; Y changes weapon; stick clicks crouch/zoom; Start pauses. The native profile is authoritative. [Inherited keyboard/mouse mappings](../port/linux/README.md#controls). The newer touch controls above supersede the inherited Android guide's old no-touch statement.

## Advanced config

Quit before external edits. In `[vr]`, `body = "legs"` explicitly selects the default; alternatives: `arms`, `full`, `hands`. Generated comments and [port_config.c](../port/linux/src/port_config.c) document all keys. Advanced settings include HUD/screen size/distance, world scale, scope size, weapon offsets, cinematic separation/convergence and diagnostics. Diagnostic switches are for development. See [the player guide](PLAYER-GUIDE.md) for paths/backups.
