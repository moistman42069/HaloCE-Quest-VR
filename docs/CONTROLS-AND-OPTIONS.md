# Controls and options - 1.0 VR / flat

These mappings follow the shipped code. Start with Controls = VR and a standard native controller profile. Changing either can change the resulting actions. Touch controllers lack conventional gamepad bumpers/View.

## Quest Touch, default VR layout

| Input | Action |
| --- | --- |
| Left stick | Move/strafe relative to Head, Left Hand or Right Hand setting |
| Right stick | Smooth/snap turn; vertical input can satisfy native look/tutorial prompts |
| Weapon-hand trigger | Fire the held gun |
| Other-hand trigger | Zoom; Scope places the zoomed view at the weapon |
| Right A | Jump / confirm |
| Right B | Reload/use in gameplay (hold for native interaction/pickup prompts); pointer-menu Back in menus |
| Left Y | Switch weapons |
| Left X with Physical weapons active | Tap/release throws; hold 0.4 seconds switches grenade type |
| Left X with Locked weapons | Switch grenade type |
| Weapon-hand grip, Locked | Throw grenade away from holsters; grip at a holster switches weapon |
| Weapon-hand grip, Physical | Hold; releasing after the initial protected grip can drop/holster/transfer |
| Other-hand grip near support region | Lock support hand in Two Hands = Grip; release detaches |
| Left stick click | Crouch |
| Right stick click | Native melee |
| Both stick clicks | Recenter during gameplay; stand normally first |
| Left menu | Pause/menu; online co-op keeps the shared world running |
| Weapon pointer + trigger in menus | Select; right B goes back |
| Off hand near head | Flashlight gesture when enabled |

Left-handed mode changes weapon/off-hand trigger roles; Touch face-button sides are not all mirrored. Palms together plus the other hand's grip can transfer handedness. Controllers with bumpers/View use weapon-hand bumper for grenade, off-hand bumper for flashlight, and View tap/hold for Back/recenter. Use the Touch-specific table above on Quest.

**Physical weapons is the offline default. MP Physical defaults Off, so network play uses Locked weapon holding and its grenade inputs even if Weapons is set to Physical.** Enabling MP Physical opts into physical holding/drop behavior; this is independent of avatar visibility.

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
| VR | Haptics 0–100%; Flashlight Gesture / Button; Holster Size 10–40 cm; Scope Off / On; Cutscenes Immersive / 3D Screen / Flat; MP Physical Off / On; Close Contact Off / On |
| Vehicles | Third Person (default) / First Person; Steering Right Hand (default) / Left Hand / Head / Stick; global and Warthog/Ghost/Banshee/Scorpion/Pelican Up/Forward/Right seat offsets ±50 cm |
| Graphics | Preset Auto / Low / Medium / High / Max; Resolution Auto / 70 / 85 / 100 / 115 / 130%; Shadows, Lights, Specular, Reflections, Bump Maps, Grass, Fog Layers: Auto / On / Off |
| Display | Decals, Particles, Contrails, Weather, Lens Flares, Camo: Auto / On / Off; Refresh 72 / 80 / 90 / 120 Hz |
| Crosshair | Native / Off; Size 25–300%; Opacity 0–100% |

Important defaults: body `legs`, arms `ik`; fingers/room-scale/holsters/scope on; hand aim/right gun hand; two-hand Grip; Physical weapons; Arm Run off; MP Physical off; Close Contact on; smooth turn 120 degrees/s; refresh request 72 Hz. Saved values override defaults. Hands Only forces hand IK even if Arms was set to hidden/animated.

Close Contact reduces only the offline local VR capsule radius: up to 15%, at most 5 cm, never below 18 cm. Solid collision and height remain. MP Physical concerns weapon holding/drop behavior, not visual avatar sharing; peers may not reproduce physical drops/pickups correctly.

Auto graphics effects follow the preset. Resolution is relative to runtime eye targets. Refresh requests a supported rate; it does not guarantee frame timing. The simulation remains 30 Hz with interpolated rendering.

## Flat Android touch and controller

The flat edition includes relative swipe aim, a draggable HUD editor, saved
positions/size/opacity/color and response settings. MOVE + FIRE/drag supports
simultaneous movement and aiming. Cancel, focus loss and hiding release touch
input. See [touch controls and editor](ANDROID-TOUCH-CONTROLS.md).

Connected Xbox-style USB/Bluetooth gamepads use Android + SDL3. Both sticks,
triggers, face buttons, shoulders, stick clicks, Start/Back and D-pad reach
Halo's native controller profile. LB is flashlight; RB switches grenades in the
default profile. Launcher **Controller & touch settings** offers independent
stick dead zones/response, trigger dead zone, vibration, optional face-button
swap and Auto / Always show / Always hide touch policies. Auto hides only for
SDL-ready full gamepads and restores touch after disconnect. Native Options
retains layout, look sensitivity and invert. No touch/gamepad setting changes VR.

See [full controller mappings, menus and testing](ANDROID-GAMEPAD.md). The
launcher/browser/dialogs support D-pad or left-stick focus navigation with
repeat, A confirm and B cancel. Device-level USB/Bluetooth, rumble and focus
validation remain pending. [Inherited keyboard/mouse mappings](../port/linux/README.md#controls).

## Advanced config

Quit before external edits. In `[vr]`, `body = "legs"` explicitly selects the default; alternatives: `arms`, `full`, `hands`. Generated comments and [port_config.c](../port/linux/src/port_config.c) document all keys. Advanced settings include HUD/screen size/distance, world scale, scope size, weapon offsets, cinematic separation/convergence and diagnostics. Diagnostic switches are for development. See [the player guide](PLAYER-GUIDE.md) for paths/backups.

## Controller calibration (test15; test20b rigid correction)

Pause > VR Settings > **Calibrate Left / Calibrate Right** (named Align Left / Align Right before test20b). These refer to the physical left/right controller, even in left-handed mode. Defaults are zero offsets and Native aim, preserving test14 poses. Correct only an affected controller; there is no firmware-based automatic flip.

**What these pages adjust:** the whole tracked controller. Since test20b the correction is applied once, rigidly, so your **held weapon and your empty hand move together**; there are no separate armed and unarmed calibrations. Before test20b, Yaw/Roll could line up the weapon but tilt the empty hand (or the reverse), because a held weapon follows the controller's aim pose and an empty hand its grip pose. Saved values are kept and the held weapon looks the same as before; only the empty hand changes, to match it. **Body** (Legs + Arms, Full, Arms + Hands, Hands Only) and **Arms** only choose what body is shown; they do not change hand or weapon alignment. **Weapons** (Locked/Physical) changes weapon handling, not calibration. The advanced `vr.weapon_offset_*` config keys place the weapon model's grip in the hand and affect only a held weapon.

- Pitch / Yaw / Roll: -180 to +180 degrees, in 5-degree steps, around controller-local X / Y / Z. Positive angles use the right-hand rule. Rotation composes yaw, pitch, roll.
- Right / Up / Back: -20 to +20 cm, in 1 cm steps, along the original controller's axes. Negative values move left / down / forward.
- Flip Roll 180: applies another half-turn around the controller's forward axis. Use this first for an upside-down hand/gun. Applying it twice returns to the prior roll.
- Aim Source (formerly Aim Pose): Native uses OpenXR's aim pose; Grip uses the grip pose as the aim source when firmware produces a bad aim pose. It changes the aiming ray as well as the weapon, so recalibrate carefully.
- Reset Left / Right: zero that controller's offsets and restore Native aim, leaving the other controller alone.

Offsets apply once per tracked frame before aiming, gesture speed, body/contact and avatar calculations. Changes clear velocity/support history so adjustment is not treated as a melee swing or run gesture. Head aim remains available. If a correction is wrong, reset that hand. These are Touch-controller calibration settings, not optical finger tracking.


## geometry and action animations

VR now defaults to **Safe geometry**, including a one-time upgrade of older
configs. Flat Android still defaults to **Normal**. Launcher **Geometry
compatibility** lets you choose either mode; restart the game afterward. Your
subsequent explicit choice is preserved. Safe mode trades some rendering speed
for compatibility. The original config is backed up during the VR migration.

Reload, grenade throw, melee, weapon draw/put-away and heat/vent actions temporarily
use the affected native arm/hand animations, then blend back to VR tracking.
Keep holding support grip to return to the same grip; releasing it allows the
hand to return to free tracking. Ordinary aiming/firing, controller alignment
and Legs + Arms remain unchanged. This is native animation playback, not physical
reload. The owner reported improved action playback in test16; the 1.0 baseline preserves it. See release notes for remaining device coverage.


## game files, revisions and server compatibility

Open **Game files & versions** to import one or more ISO/XISO images, select an
extracted maps folder, or scan the displayed `game-versions/inbox` folder. Each
complete set shows detected cache region/build and a SHA-256 fingerprint. Select
**Use** to activate it for the next launch; **Rename** edits your personal label.
The original installation remains **Existing game data**. Saves stay separate
per set, and current settings are copied once into a newly imported set.

Some server incompatibilities may result from different ISO/revision map files
or modified data. Network protocol versions, missing maps, full/closed hosts and
NAT can also prevent joining. Original/Rev1/Rev2 labels are not automatically
verified without trusted hashes. The browser can offer another installed set
containing a missing map, but servers do not advertise authoritative revision or
content fingerprints. Do not change map headers to bypass compatibility checks.

Test17 addresses false rejection of running v11 matches, an action-control
assertion, and reviewed departed-player/rejoin issues. The test16 animation
handoff is preserved. [Full data-library instructions](GAME-DATA-LIBRARY.md).

## Vehicle controls and opening tutorial (test18)

- **Vehicles:** third-person chase and right-controller steering default. **VR Settings > Vehicles** selects Third Person / First Person and Right Hand / Left Hand / Head / Stick steering. Left stick supplies movement/throttle; the selected physical controller points the driving direction independently of weapon handedness or support grip. Tracking loss holds native facing. Gunners retain head aiming.
- **First-person seats:** level horizon with head leaning; Up, Forward and Right adjustments in 1 cm steps, ±50 cm. Global offsets plus Warthog, Ghost, Banshee, Scorpion and Pelican profiles; custom vehicles use global values. Combined offsets clamp to ±50 cm per axis and are shortened at map collision. Zero restores the native seat location. Offsets affect First Person only. First-person heading follows the vehicle; chase steering uses the world heading with normal stick turns.
- **Upgrade defaults:** the first test18 VR launch applies chase/right once and backs up the prior settings as `config.toml.pre-vehicle-defaults`. Your subsequent vehicle choices persist. Other body, grip, action and graphics preferences are retained.
- **Other views:** immersive, 3D-screen or flat cinematics; native crosshair artwork with size/opacity or Off.
- **Opening look tutorial:** look toward the lights with your headset. Script gaze and head-movement checks use the tracked head, independently of the weapon reticle. This is headset direction, not eye tracking.
