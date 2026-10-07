# Test31: complete OpenCE in-game menu inventory

Source audit, 2026-10-07. Pinned OpenCE **Build 145**, commit
`4e8ed2f196e0edd1f2830a4de9841686aabbf466`, network 22. This is an
implementation inventory, not a claim of device validation. The owner now
requires the complete in-game menu setup in the next candidate; launcher
features are supplementary. APK packaging remains held for all three prompts.

## Findings that change the plan

- The pinned manifest has **50 XML files and 883 widget definitions**. The old
  handoff's 55-file count is stale. Three XMLs are shared resources; the other
  files contain screens, subcomponents, generated overrides or compatibility
  wrappers, rather than exactly one screen per file.
- `UNWIRED.md` and parts of the menu README are stale. The implementation
  actually wires server browsing, hosting, passwords, gametype editing and
  local split-screen. Determine behavior from `menu_functions.c` and the XML.
- Conversely, the browser's **Filters, Update, mode selector, sorting arrows
  and column sorting are deliberately disabled upstream**:
  `browser_initialize` hides them. Importing their XML does not make them
  functional. Preserve the owner's most-populated-first requirement separately;
  expose no inert filter buttons as working features.
- OpenCE's **CO-OP CAMPAIGN** item is local, two-player split-screen. Internet
  campaign hosting is **CREATE GAME → INTERNET → campaign map/difficulty →
  SERVER SETUP**. These must be clearly distinguished on Quest. A headset does
  not establish a second independent local view. If local split-screen cannot
  be supported on VR, show an explicit limitation and the online hosting path.
- Direct Link is the port's invite-link path. The inherited Direct IP XML
  filename is not evidence of a functioning arbitrary IP/password connector.
  Joining uses `p2p_join_invite` and the native network client.

## Source and build dependency set

| Area | Required integration |
| --- | --- |
| Generated menu tags and actions | Add `port/linux/game/menu_tags.c`, `menu_functions.c` and `port/linux/include/halo_menus.h`. Guest game-source enumeration picks up the game files. |
| XML/PNG loading | Add `port/linux/src/menu_files.c`, `menu_files.h`; include all `port/assets/menus` files named by `menus.json`, plus upstream generation/credit documentation. Runtime does not need to run asset generators. |
| XML parser | Import `port/third_party/expat` headers, configuration, sources and license. `android_build.py` and `linux_build.py` compile `xmlparse.c`, `xmlrole.c`, `xmltok.c` with that include directory and the platform ABI. |
| Asset embedding | Merge menus manifest/files into `tools/embed_assets.py`, including configure dependencies. Preserve the app's existing HUD/title/font embedding. |
| Asset maintenance | Take `tools/ce_menus.py`, `tools/port_settings.py` as appropriate for reproducibility; do not regenerate from absent private CE assets just to compile. Keep redraw/font/source credits. |
| Cache lifecycle | Add `cache_files_tag_instances` / `cache_files_set_tag_instances`; invoke `menu_tags_loaded` only after the selected stock/CE map tags exist, and `menu_tags_unloaded` before those tags are destroyed. Upstream load hooks are in `source/cache/cache_files.c` at 1173/1262, unload at 606. Preserve the app's loader and allocation budget. |
| Texture draw | Merge `menu_art_texture` into `port/linux/src/xbox_textures.c` (upstream line 883). `menu_files.c` uses the existing high-resolution HUD PNG decoder and GL abstraction. Preserve Android upload/performance fixes. |
| Widget engine | Merge PC screen-root selection, tag/frame recognition, child-focus traversal, spinner mouse handling, deferred button posting, custom event dispatch and `ui_widget_port_*` helpers into `source/interface/ui_widget.c`. Keep current VR ray selection, face-button routing, safe error text and pause behavior. |
| Widget dispatch | `ui_widget_event_handler_functions.c` dispatches IDs starting at `PC_MENU_FUNCTION_BASE` (256), and supplies profile/map/gametype/host/join adapters. `ui_widget_game_data_input_functions.c` dispatches the matching data functions and understands PC descriptions/lists. Keep VR menu function IDs separate. |
| Text and map thumbnails | Merge `source/text/text_group.c` recognition of PC copies of campaign/map strings. Adapt the current `custom_edition_maps.c/.h` API; avoid wholesale replacement of the app's `.yelo`, managed sets or PAL paths. |
| Configuration | Add `display.menus` default `pc`, fallback `xbox`, and opt-in `debug.menu_open`; review each settings key below against this port's actual consumer. A spinner writing an unused key is not completion. |
| Platform services | Add/adapt `platform_display_resolutions`, `platform_window_sizes`, `platform_display_apply`, `platform_binding_capture_begin/poll`, `platform_clipboard_get/set` and `platform_text_field`. The implementations live in upstream `sdl_platform.c` and `xinput_sdl.c`; do not replace those files wholesale. |
| Network | Reuse current native P2P listing/password API, host/client lifecycle and protocol 22. Retain application avatar extensions, stock-peer compatibility gates and existing launcher hosting. Do not create a second protocol or directory. |

The menu files do not require wholesale adoption of the new desktop tag
validator or CE loader. They do require the **map listing API**, appended tag
table ownership, and adapters for the current renderer/input backends.

## Every XML file accounted for

Paths are under `port/assets/menus/ce/`. The exact filenames below are the
manifest inventory. “Import/adapt” is planned work, not a completed status.

| File | Functionality / treatment |
| --- | --- |
| `bitmaps.xml` | Shared menu art definitions, including map-frame fallbacks. Import. |
| `strings.xml` | Shared labels, help, option values and descriptions. Import; correct mobile/VR text where needed. |
| `shell.xml` | Shared shell widgets. Import. |
| `error.xml` | Confirm delete profile/gametype/save; saving/profile creation; legacy video confirmation dialogs. Preserve real confirmations and adapt obsolete desktop video messaging. |
| `main_menu.xml` | Campaign, multiplayer, settings, profiles, quit navigation. Add/retain reachable VR Settings. |
| `main_menu.campaign_select.xml` | Continue/New/Load campaign, save listing and deletion. Keep existing saves and profile selection. |
| `main_menu.difficulty_select.xml` | Easy/Normal/Heroic/Legendary selection and start. |
| `main_menu.new_select.xml` | New campaign map list and level descriptions. |
| `main_menu.new_select.port.xml` | Stock/custom single-player map-kind override. Requires map adapter. |
| `main_menu.solo_level_select.xml` | Campaign level selection/description. |
| `main_menu.gametype_select.xml` | Multiplayer gametype bank/list selection. |
| `main_menu.player_profiles_select.xml` | Player profile list and creation entry. |
| `main_menu.profile_manager.xml` | Active profile, create and confirmed delete. Preserve test30 X-delete/B-back fixes. |
| `main_menu.quit_select.xml` | Quit confirmation; return/close Android activity through existing platform lifecycle. |
| `main_menu.multiplayer_type_select.xml` | Create Internet/LAN, join Server Browser/LAN/Direct Link, Edit Gametypes, local co-op. Clearly distinguish local and network campaign. |
| `main_menu.multiplayer_type_select.connected.xml` | Connected-flow wrapper compatibility. Keep referenced wrappers. |
| `main_menu.multiplayer_type_select.connected.4way_profile_select.xml` | Local profile-selection wrapper. Explicit Quest local-player limitation if unsupported. |
| `main_menu.multiplayer_type_select.coop.xml` | Local split-screen player-two profile screen. Not the online co-op host UI. |
| `main_menu.multiplayer_type_select.direct_ip.xml` | Legacy direct-IP/password layout. Actual supported port action is Direct Link; no false raw-IP claim. |
| `main_menu.multiplayer_type_select.join_game.xml` | Native LAN/P2P directory browser, server rows/status, join, refresh, errors and scrolling. Keep population-first ordering. |
| `main_menu.multiplayer_type_select.join_game.filters.xml` | Legacy full/empty/type/team/missing-map/ping filter layout. Inert upstream; implement deliberately or visibly identify unavailable controls, not pretend they work. |
| `main_menu.multiplayer_type_select.join_game.port.xml` | Browser header, Direct Link clipboard action and password screen. All text paths need controller/touch/VR entry. |
| `main_menu.multiplayer_type_select.lobby.xml` | Player roster, teams, start/countdown, leave, add local player, in-progress preview and join. 128 roster entries must remain scrollable. |
| `main_menu.multiplayer_type_select.mp_map_select.xml` | Stock/custom multiplayer and campaign maps; campaign difficulty step. |
| `main_menu.multiplayer_type_select.server_settings.xml` | Name, max players, invite copy, public/private listing, public password, gametype options; campaign friendly fire/enemy scaling/player collisions. |
| `main_menu.settings_select.multiplayer_setup.xml` | New gametype creation wrapper. |
| `main_menu.settings_select.multiplayer_setup.playlist_select.xml` | Stored gametype list, create, edit and confirmed delete. |
| `main_menu.settings_select.multiplayer_setup.playlist_edit.xml` | Gametype name and subpage hub, save/cancel. |
| `main_menu.settings_select.multiplayer_setup.name_edit.xml` | Gametype naming using native keyboard flow. |
| `main_menu.settings_select.multiplayer_setup.playlist_edit.game_type_select.xml` | CTF, Slayer, Oddball, King of the Hill and Race engine selection. |
| `main_menu.settings_select.multiplayer_setup.playlist_edit.ctf_edit.xml` | Captures, home flag, reset/single-flag and time options. |
| `main_menu.settings_select.multiplayer_setup.playlist_edit.slayer_edit.xml` | Score/team rules, kill penalties/order and Slayer options. |
| `main_menu.settings_select.multiplayer_setup.playlist_edit.oddball_edit.xml` | Ball count/type, score/time, random start, speed and carrier/noncarrier traits. |
| `main_menu.settings_select.multiplayer_setup.playlist_edit.koth_edit.xml` | Hill score/movement/team options. |
| `main_menu.settings_select.multiplayer_setup.playlist_edit.race_edit.xml` | Lap count, race type and team rules. |
| `main_menu.settings_select.multiplayer_setup.player_options_edit.xml` | Shields/health, invisibility, respawn/time growth, suicide penalty and odd-man-out. |
| `main_menu.settings_select.multiplayer_setup.item_options_edit.xml` | Starting equipment and weapon-set page. |
| `main_menu.settings_select.multiplayer_setup.item_options_edit.port.xml` | Map weapons, category/custom loadout, primary/secondary weapon choices. |
| `main_menu.settings_select.multiplayer_setup.vehicle_options_edit.xml` | Side/team, Warthog/Rocket Warthog/Ghost/Scorpion/Banshee/turret and respawn options. Preserve app CE vehicle handling. |
| `main_menu.settings_select.multiplayer_setup.indicator_options_edit.xml` | Friendly indicators and radar visibility. |
| `main_menu.settings_select.multiplayer_setup.teamplay_options_edit.xml` | Friendly fire/penalty and automatic balance. |
| `main_menu.settings_select.player_setup.player_profile_edit.xml` | Profile/settings hub, About, name/color, controls/gamepad/mouse/audio/video/network, OK/cancel. VR Settings remains reachable. |
| `main_menu.settings_select.player_setup.player_profile_edit.name_edit.xml` | Profile name using native on-screen keyboard. |
| `main_menu.settings_select.player_setup.player_profile_edit.color_edit.xml` | Profile color picker, all 18 colors and scrolling. |
| `main_menu.settings_select.player_setup.player_profile_edit.controls_setup.xml` | Keyboard/mouse rebinding, 17 actions in three groups, two bindings per action, defaults/clear/cancel. Explain scope; keep touch and VR mappings separate. |
| `main_menu.settings_select.player_setup.player_profile_edit.gamepad_setup.xml` | Profile look sensitivity, look/flight inversion, autocenter, five button presets, four stick layouts, vibration/help. Preserve Android dead zones, reconnect and overlay policy. |
| `main_menu.settings_select.player_setup.player_profile_edit.mouse_settings.xml` | Horizontal/vertical sensitivity, vertical inversion and mouse aim assist. Available to a real external mouse; no implication these adjust tracked controllers. |
| `main_menu.settings_select.player_setup.player_profile_edit.audio_settings.xml` | Master/music/effects volume, reverb, audio enabled, defaults/save. |
| `main_menu.settings_select.player_setup.player_profile_edit.video_settings.xml` | Desktop-only display rows plus Android/shared rendering settings; full treatment below. |
| `main_menu.settings_select.player_setup.player_profile_edit.network_setup.xml` | Online, UPnP, clipboard invites, update check, player names/size, scoreboard layout/background. Route update policy to validated app updater. |

## Settings needing explicit mobile / Quest treatment

### Video

Upstream marks display mode (fullscreen/borderless/windowed), output resolution,
window size, resolution scaling, desktop FPS limit and direct-camera rows
`platform="desktop"`. Retain that truth in Android. Offer the app's actual
mobile render scale/FPS and Quest resolution/refresh/comfort options through
appropriate in-game settings, not nonfunctional desktop controls. Do not
reconfigure the OpenXR swapchain via a desktop display-mode save.

Shared upstream rows: V-sync, interpolation, high-resolution HUD/text, shadow
resolution (128/256/512/1024), per-pixel lighting. Check actual consumers and
Quest performance constraints before exposure. VR's accepted geometry-safe
default and native refresh scheduling must survive Default/Save actions.

Upstream Android AA offers Off/FXAA/MSAA 2x/MSAA 4x; desktop also has SMAA,
SSAA 2x and MSAA 8x. A menu import does not prove those pipelines exist in
this app. Bind to supported flat/VR renderer choices and explain unavailable
ones. Preserve established Quest MSAA and render-upload behavior.

### Controls and text

Keyboard binding groups are Movement (forward/back/strafe/jump/crouch), Combat
(fire/grenade/melee/reload/zoom/switch weapon/switch grenade), and Actions
(use/flashlight/scoreboard/pause). Two slots per action; left/right select
slot, capture takes a key/mouse input, Escape cancels and Delete clears.
Quest trigger clicks must not accidentally rebind to a synthetic mouse button.

OpenCE gamepad settings edit profile fields, while this app additionally has
VR action mappings and Android controller/dead-zone/touch-overlay settings.
Keep their ownership clear and make each reachable. Keyboard/mouse and local
split-screen availability should be described per edition.

Profile and gametype names use the game's existing on-screen keyboard path.
**Server names and passwords use a different text-field implementation**:
`text_field_begin` calls `platform_text_field(TRUE)`, then
`text_field_show` consumes `input_get_key` ASCII/backspace/Ctrl-V. It does
not create an on-screen keyboard. Merely importing `platform_text_field`
would leave touch-only/Quest users unable to enter these fields. Bridge them
to an accessible native/widget or Android input surface with accept/cancel,
length enforcement and masked passwords. Losing the screen, Back, joining,
map unloading and focus loss must stop capture and release input ownership.

The app already bridges SDL clipboard via Android guest/host. Add the menu
wrappers without a new clipboard implementation. Copying an invite must not
post it externally or put its private value into logs.

### Network / hosting

Server Setup supports up to 128 players (not a performance guarantee),
public/private visibility and a 32-character public password. Campaign has
friendly fire Off/On/Shields only/Explosives only; extra enemies None/Per player/
Static multiplier; per-player 25/50/100/150/200%; multiplier 2/4/8/16/32x;
player collisions On/Off. These are existing upstream network settings, not
permission to enable expensive extremes by default. Preserve current defaults.

The upstream browser keeps 256 listings, 15 visible rows, a 30-second join
timeout, and scrolls. It filters invalid signed listing names and uses the
native invitation handshake. Keep exact network version checks, missing-map
guidance, content/revision warnings and password handling. Reordering a list
must preserve the selected server by stable identity rather than row number.

Network Setup's `update.auto` must refer to the app's validated release path.
Do not enable blind installation of upstream desktop/network components by
adding an inherited spinner. Scoreboard layout/background options need the
upstream scoreboard consumer (review separately), or an honest unavailable
state; writing the keys alone does nothing.

## CE / tag / pause integration risks

- Upstream map display indices reserve stock multiplayer below `0x1000`, stock
  campaign at `0x3000`, CE multiplayer at `0x4000`, CE campaign at `0x6000`.
  Current app only exposes the older limited CE multiplayer API. Add bounded
  adapters; preserve its supported `.map`/`.yelo`, active managed set and
  resource-map policy. Keep `custom_maps\\name` protocol names distinct from
  stock campaign/multiplayer names. A campaign header is not proof of playable
  custom scripting or compatibility.
- `menu_tags.c` owns an appended heap tag table and art placeholders. Release
  order must be checked beside `vr_menu.c`, which also modifies runtime tags.
  Do not free a table still referenced by either menu, or restore a stale table
  after map switch. Keep failure limited to menus and preserve stock fallback.
- Upstream `pause_patch` adds Settings and host End Game to the multiplayer
  collection; it does not generically rebuild every campaign pause screen.
  Keep campaign/co-op VR Settings reachable, no duplicate buttons, adequate
  bounds, and multiplayer clocks running while menus are open.
- Upstream PC widget structs duplicate engine layouts. Preserve ABI widths,
  padding and event numbering; compile is necessary but not enough to prove
  synthetic tag traversal is safe on Android's guest ABI.
- Placeholder artwork and map-frame fallbacks are intentional upstream.
  Import only public generated assets and required licenses. Do not bundle
  copyrighted game maps to obtain the remaining frames.

## Acceptance gates for the full import

1. Parse every manifest XML for Android; validate named references/events and
   make all supported settings have a real consumer. Test malformed XML and
   missing art fall back without destroying VR/session state.
2. Exercise navigation with synthetic widgets: select/back once, disabled and
   hidden items, scroll boundaries, spinners both directions, profile/gametype
   deletion, confirmation/cancel and server sorting with selection identity.
3. Exercise typed field lifecycle, masking/limits, accept/cancel, stale field
   timeout, clipboard handling and key-capture isolation from gameplay.
4. Test map classification/display names independently from disk load; namespaced
   CE and stock same-name maps must stay distinct, including managed `.yelo`.
5. Test host/browser flows through actual native APIs: campaign and PvP, player
   counts/settings, private/password games, mismatch/missing maps, leave/rejoin,
   in-progress join and host End Game. No real networking claim from stubs.
6. Compile both variants and re-run existing profile/input/VR/pause/network
   regressions. APK packaging remains held until all owner prompts are complete.
7. On devices: Quest laser, A/B/X/Y and sticks; Android touch-only and external
   gamepad; text entry without keyboard; all profile/campaign/settings paths;
   public/private/password co-op and PvP; pause without freezing peers;
   menu→game→menu repetition; long lists and readable panels at headset scale.

These gates distinguish implementation checks from the owner's eventual device
acceptance. No headset, phone or live cross-play session is asserted here.

## Map adapter implementation (2026-10-07)

`custom_edition_maps.c/.h` now implements the upstream menu API against the
existing **active managed set**, including stock campaign display entries,
separate CE campaign/multiplayer lists, PC map-name display categories and
the protocol's `custom_maps\\name` namespace. It retains `.map` before `.yelo`
precedence, existing header classification and the existing resource loader.
The added `custom_edition_cache_campaign` query checks a valid CE header's
solo scenario type; it changes no loading or conversion behavior.

The old 25-character filename restriction came from the previous duplicated
`levels\\test\\name\\name` representation. The new namespace permits **51
filename characters**, keeping the entire network level name within 63.
Stock and CE maps named `a30` or `bloodgulch` remain distinct.

The scanner retains the existing **128 CE multiplayer map** memory budget,
with a separate **128 CE campaign header** budget. This differs from upstream
desktop's 8,192 multiplayer and 1,024 campaign entries; it is a bounded Quest
memory choice, unrelated to the network player limit. Overflow is logged.
No supported existing map count was reduced. “Vanilla” classifies conventional
PC map filenames, not authenticated unmodified content.

Scans are cached across menu frames, invalidated when a list opens or the
managed root changes, with old thumbnails released. The new focused suite,
`tools/test_test31_menu_maps.py`, compiles the production scanner with
ASan/UBSan and synthetic enumeration/classification: stock/CE names, campaign
indices, `.yelo` selection, duplicate precedence, filename/list bounds, null
inputs, active-set refresh and no scan churn passed. Real parser/resource
tests and the full Android build remain separate; custom campaign playability
and devices are not established by this test.
