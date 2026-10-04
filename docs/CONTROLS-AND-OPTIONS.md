# Controls and options - 1.0 VR / flat

These mappings follow the shipped code. Start with Controls = VR and a standard native controller profile. Changing either can change the resulting actions. Touch controllers lack conventional gamepad bumpers/View.

## Quest Touch, default VR layout

| Input | Action |
| --- | --- |
| Left stick | Move/strafe relative to Head, Left Hand or Right Hand setting (right stick when left-handed, below) |
| Right stick | Smooth/snap turn; vertical input can satisfy native look/tutorial prompts (left stick when left-handed) |
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

**Left-handed (test20d):** Controls → **Handedness: Left** puts the gun in the left hand and, with **Mirror Controls: Auto** (default), mirrors the whole table above: move on the right stick, turn on the left, jump on left X, reload/use on left Y, switch weapons on right B, grenades on right A, crouch on the right stick click, melee on the left stick click, and Back in menus on left Y. Triggers, grips, zoom, flashlight, holsters and the menu pointer already follow the gun hand. Switching Handedness in the menu also moves vehicle **Steering** and **Move With** to the other hand when they were set to a hand. **Mirror Controls: Off** keeps the right-handed button layout with the gun in the left hand. A config that was already left-handed before test20d keeps its standard buttons (Mirror Controls Off) until you change it. Palms together plus the other hand's grip still pass the gun across. Controllers with bumpers/View use weapon-hand bumper for grenade, off-hand bumper for flashlight, and View tap/hold for Back/recenter. Use the Touch-specific table above on Quest.

**Physical weapons is the offline default. Weapons: Physical keeps network play on Locked weapon holding and its grenade inputs; Physical + MP opts multiplayer into physical holding/drop behavior.** This is independent of avatar visibility.

Physical weapons is the local default. A gun supplied on load/pickup stays supported until the first grip. Two Hands = Grip requires a squeeze near the support area; simply touching the barrel does not attach. Auto restores proximity attachment; Off disables it. The support point remains fixed until release.

## Gestures

- Crouch compares height against the last recenter; default 35 cm, zero disables physical crouch.
- Flashlight gesture: off hand within 20 cm of the head by default. Button mode disables proximity activation.
- Shoulder/hip holsters: default region size 20 cm, with entry haptics. Locked and Physical modes use them differently as above.
- Arm Run defaults off. Pumping or two-hand weapon bob supplies forward movement with a neutral stick. A lower Arm Run number (Easy 0.3) makes activation easier. Strong offline effort can reach 1.5x speed; network speed stays stock. Stick input wins.
- Impact melee sweeps the hand/weapon; Swing requests native melee. Default threshold 2 m/s, zero disables motion melee. The button still works. Network clients use Swing.
- Local finger poses use controller touch/trigger/grip sensors. Free-hand point/thumb/fist and a held gesture are available; this is not optical tracking of individual fingers.
- Full-body IK infers untracked joints. Legs + Arms hides the local chest and retains legs/first-person arms. Supporting peers can still see the full body.

## VR settings

Open the stock campaign pause menu, then **VR Settings**. Screens have four rows per column and reserved navigation space. **Next Page** opens the next screen; Back returns through pages/categories. A/right increases/advances; left decreases. Numeric endpoints clamp; changes save to `config.toml`.

| Category | Menu options |
| --- | --- |
Test20d gives each decision one row. Rows that only mattered together with another are combined: Turning includes the turn speed, Holsters the holster size, Weapons the multiplayer choice, Arm Run the effort, and Hands the old Arms row. The Crosshair rows moved to Gameplay, and the Left Hand, Right Hand and Gun pages became **Hands + Gun**. A combination set by hand in `config.toml` that matches no choice shows as **CUSTOM**. Pressing the row picks the first choice.

| Category | Menu options |
| --- | --- |
| Controls | **Handedness** Right / Left; **Mirror Controls** Auto / Off; **Turning** Smooth 60–300 degrees/s or Snap 30 / 45 / 90; Move With Head / Left Hand / Right Hand; **Two Hands** Auto Lock (default) / Squeeze / Off; **Weapons** Locked / Physical / Physical + MP; **Holsters** Off or 10–40 cm; Aim Hand / Head; Controls VR / Xbox |
| Body | Body Arms + Hands / Full / Legs + Arms / Hands Only; **Hands** Body IK / Floating / Float + Arms / Animated / Gun Only; Fingers Off / Tracked; Room-scale Off / On; Crouch Depth Off or 5–40 cm; **Arm Run** Off or effort 0.3–1.2; **Melee** Impact / Swing / Impact + Online / Swing + Online; Melee Speed Off or 1.0–3.6 m/s |
| Hands + Gun | Hand Pitch / Yaw / Roll (both hands, left mirrored; default −70 / 0 / 0); Reset Hands; Gun Pitch / Yaw / Roll (default 0); Reset Gun; Gun Forward / Up / Out ±20 cm; Gun Grip Anchored / Classic |
| Gameplay | Haptics 0–100%; Flashlight Gesture / Button; Scope Off / On; Cutscenes Immersive / 3D Screen / Flat; Close Contact Off / On; Crosshair Native / Off; Crosshair Size 25–300%; Crosshair Opacity 0–100% |
| Vehicles | Third Person (default) / First Person; Steering Right Hand (default) / Left Hand / Head / Stick; global and Warthog/Ghost/Banshee/Scorpion/Pelican Up/Forward/Right seat offsets ±50 cm |
| Graphics | Preset Auto / Low / Medium / High / Max; Resolution Auto / 70 / 85 / 100 / 115 / 130%; Shadows, Lights, Specular, Reflections, Bump Maps, Grass, Fog Layers: Auto / On / Off |
| Display | Decals, Particles, Contrails, Weather, Lens Flares, Camo: Auto / On / Off; Refresh 72 / 80 / 90 / 120 Hz |
| Controller Left / Right | Advanced tracking correction for hand and gun together (see below) |

Important defaults: right-handed with Mirror Controls Auto; body `legs`; Hands Body IK; hand pitch −70°; gun angle 0, Gun Grip Anchored, gun position 0; fingers/room-scale/scope on; holsters 20 cm; hand aim; two-hand Auto Lock; physical melee offline only; Physical weapons (not in multiplayer); Arm Run off; Close Contact on; smooth turn 120 degrees/s; refresh request 72 Hz. Saved values override defaults. Hands Only forces hand IK even if Hands was set to Animated or Gun Only.

Close Contact reduces only the offline local VR capsule radius: up to 15%, at most 5 cm, never below 18 cm. Solid collision and height remain. Physical + MP concerns weapon holding/drop behavior, not visual avatar sharing; peers may not reproduce physical drops/pickups correctly.

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

## Two hands, melee and the horn (test21)

- **Two Hands: Auto Lock** (new default): rest the off hand at the gun's support grip (where Halo's animation puts that hand) for about a tenth of a second and it locks there, as a squeeze used to. Pull the hand away (the hands' distance changes by 20 cm, or the hand leaves a 60-degree cone ahead of the gun) to release; it locks again only after the hand has left the grip. **Squeeze** is the old behaviour (lock while the grip is held at the support); **Off** never attaches. A config still on the old Grip default moves to Auto Lock once; a later choice is kept.
- **Melee online:** physical melee (Impact or Swing) is off in network games by default, because a quick hand movement there (reaching for a holster) could melee. The melee button (right stick click) always works. Body → Melee: **Impact + Online** / **Swing + Online** turns physical melee on in network games too.
- **Horn:** a driver's horn is Halo's crouch control. While seated, either stick click sounds it, whatever the throttle (the game used to pass the left stick click only below 98% throttle, and the Warthog's throttle is that stick). Clicking both sticks still recentres. A lowered head no longer counts as crouching while seated.

- **Upside-down hands or guns** (reported on Quest OS v78): use **Controller Left/Right → Flip Roll 180** for the affected controller; it turns hand, gun and two-hand aim together. Hand Roll turns only the visible hand and Gun Roll only the gun; since test21 Gun Roll also holds in two-hand grip (it used to flip back).

## Shots, reticle and per-gun aim (test21)

- **Pistol shots from the hand.** Some guns (the pistol among them) tell the game to start their shots at the gun model's own muzzle. In VR that was the unseen third-person body's gun, so the shots flew beside the reticle. Offline, with the hand aiming, such shots now start at your hand like every other gun's. Network play is unchanged (the host decides shots there).
- **Reticle includes each gun's shot offset.** Halo shifts some guns' shots a few centimetres off the aim line (each gun's tag sets it). The reticle now includes that shift, so it marks where shots actually go.
- **Aim For / Aim Up / Aim Right / Reset Aim** (Hands + Gun, second screen): fine-tune the gun you are holding. Aim For shows which gun the rows change (Pistol, Plasma Pistol, Assault Rifle, Plasma Rifle, Shotgun, Sniper Rifle, Rocket Launcher, Needler, Fuel Rod, Flamethrower, or Other Gun for custom maps). Aim Up/Right move that gun's shots, reticle and scope together in half-degree steps up to 10 degrees; the gun model stays where it is. Reset Aim sets that gun back to 0. Each gun keeps its own values (`vr.aim_<gun>_up` and `_right` in config.toml), the same in either hand.

## Body turns and Full Body (test21)

- The arms hang from shoulders that face the torso in every Body mode. Before, without a drawn body (Arms + Hands, Hands Only), the shoulders faced the stick-turn heading, so turning your real body left them behind and the arms twisted across.
- The torso's direction follows the head beyond a 15-degree comfort cone (25 before), drawn halfway toward your hands when both are tracked ahead, so turning your body (head and hands together) turns it while looking around with the head alone mostly does not. The head's direction is read so it stays steady even looking straight down; it used to flip there and snap the torso.
- Full Body hangs from a neck pivot 14 cm behind and 20 cm below your eyes in the head's own frame. Looking down swings the eyes forward and down about it, so the chest stays behind and below them instead of moving into the camera. Legs + Arms stays the default until Full Body is confirmed on a headset.

## Hand, gun and controller calibration (test20c, test20d)

Three separate things can be adjusted in Pause > VR Settings. Each changes only what its name says:

| Rows | Changes | Never changes |
| --- | --- | --- |
| **Hands + Gun → Hand Pitch / Yaw / Roll** | How the visible empty (or free) hands sit on the controllers. One row turns both hands; the left is the mirror image (same pitch, opposite yaw and roll). Default **−70 / 0 / 0**, taken from the owner's 2026-10-04 calibration video, so the glove lines up with a real hand holding a Touch controller. Different values per hand can still be set in `config.toml` (`vr.hand_left_*`, `vr.hand_right_*`). | The gun, its shots, the reticle, gestures |
| **Hands + Gun → Gun rows** | Gun Pitch / Yaw / Roll: the one-handed gun's angle on the controller (default 0). Shots and the reticle turn with the gun, mirrored for the left hand. With both hands on the gun, the line between the hands aims it, as before. Gun Forward / Up / Out: where the gun sits in the hand (default 0; Out means away from your body's middle, so it mirrors for the left hand). Gun Grip: Anchored (default) or Classic (below). | The empty hands |
| **Controller Left / Right** | Advanced tracking correction for a misreported controller: rotates/moves **hand and gun together** (one rigid correction since test20b). Flip Roll 180, Aim Source, Reset. Normally leave at zero. | — |

**Gun anchored to the controller (test20d).** The first-person gun is drawn from a "weapon camera" placed 20 cm behind, 12 cm above and 10 cm beside the controller's grip. Each weapon's animation then puts the gun hand somewhere in front of that camera, so where the gun sat in your hand depended on the weapon. The pistol sat ahead of, above and inward of the real controller in the owner's passthrough video, and because it turned around the camera rather than your hand, it swung as you turned your wrist. With **Gun Grip: Anchored**, every frame the whole first-person model (gun, hands and arms together) moves so that the gun hand's wrist is exactly where your empty hand's wrist is. The gun then turns about your hand. This works the same way for every weapon. Nothing is tuned per weapon: each weapon's own animation decides how the gun sits in the hand, and the anchor only moves that hand to your controller. During reload, melee, grenade throws and drawing a weapon, Halo's animation plays around your hand, and the gun returns to it within about 0.05 s afterwards. Pulling the gun back from a wall still works. **Classic** restores the older placement for comparison. The legacy `vr.weapon_offset_*` keys only position the weapon camera now; they no longer move an anchored gun.

**Upgrading:** test20c moved any rotation you saved on the old Calibrate / Align pages into the hand rotation, once. Test20d keeps every saved value. Your Gun Pitch / Yaw / Roll stay as you set them, but they were tuned while the gun sat in the wrong place, so use **Reset Gun** before judging the new grip. Each game-data set has its own settings file, so this happens per set.

**Hand tracking** (Body page → **Hands**), separate from what body is shown:

- **Body IK** (default): unchanged. Arms reach from the body's shoulders; with Full or Legs + Arms the hands follow the body solution.
- **Floating:** hands only, exactly where the controllers are, whatever the Body setting (test21 restores test20c's meaning; test20d had merged it with Float + Arms, which drew arms). The glove cuff closes just behind each wrist along the hand's own direction, so the wrist no longer looks cut or slivered.
- **Float + Arms:** hands exactly at the controllers, with arms hanging from a shoulder that floats with the hand (it stays at the body's shoulder within reach and slides along beyond it). With Body: Hands Only it behaves as Floating.
- **Animated:** Halo's own arm animation (the old Arms = Animated); the gun is still anchored.
- **Gun Only:** arms and hands hidden (the old Arms = Hidden).

In every mode, a held gun stays in the gun hand, the support hand stays locked to the gun while gripping, and reload/grenade/melee animations take over the hands as before. **Hands Only** gathers the hidden arm behind each wrist instead of toward the elbow, so the glove no longer looks cut off. **Body** and **Hands** never change calibration; **Weapons** (Locked/Physical) changes weapon handling only.

### Controller Left / Right details (test15)

These refer to the physical left/right controller, even in left-handed mode. Defaults are zero offsets and Native aim, preserving test14 poses. Correct only an affected controller; there is no firmware-based automatic flip.

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
