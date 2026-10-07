# Test31 in-game menu scope and implementation

Status: owner superseded the earlier narrow approval on 2026-10-07:
**EVERYTHING from OpenCE's in-game menu setup must reach this build.**
Import/adapt the full in-game setup, not launcher-only equivalents. The launcher
may be adjusted as needed. The owner's latest instruction allows packaging
after this full menu work, turret/window fixes and upstream/network integration
are complete and validated, before the later interaction workstreams.

## Current implementation

Pinned Build 145's menu modules, 50 XML files, bitmap assets and Expat parser
are integrated. App adapters connect campaign/profiles, map selection,
Server Setup, saved gametype options, browser filters and exact protocol gates,
settings persistence and real audio/graphics/scoreboard consumers. Quest laser
and buttons, physical gamepads, Android direct touch/mouse and native keyboard
entry share the menu actions; current launcher flows and VR Settings remain.

The standalone legacy Direct IP XML remains a compatibility asset; the actual
multiplayer join choices are SERVER BROWSER, LAN and DIRECT LINK (PASTE LINK or
Android/Quest ENTER LINK). The known-map filter uses the cached catalog, while
join preflight checks the actual required map. No per-frame directory scan or
fabricated public-server ping was added.

Android's inert desktop update toggle is replaced by USE LAUNCHER guidance to
the validated APK updater. Desktop display modes/resizing are excluded from
Android; VR synchronization remains OpenXR-owned. Full schema validation and
the desktop CE loader are separate deferred engine changes, not hidden menu
settings. See [TEST31-MENU-SETTINGS-AUDIT.md](TEST31-MENU-SETTINGS-AUDIT.md) for
consumer coverage and [TEST31-UPSTREAM-DECISIONS.md](TEST31-UPSTREAM-DECISIONS.md)
for the retained loader/platform boundaries.

The final combined run passed all 47 suites plus 127 cache-format tests
(4 skipped). This includes parser/assets, source map catalog, text-entry
lifecycle, filters/sort/selection, configuration/profile persistence, pointer
coordinates, graphics fallback, tag teardown, solo pause and Quest local-player
guards. Both APKs are built and signed; see TEST31-DELIVERY.md for provenance.
Real navigation and cross-play acceptance still need the owner's device sessions.

The alternatives below are historical planning context. The full scope above
is now the owner's instruction and does not require another scope approval.

## Historical option A: browser and Server Setup first (superseded)

Expose OpenCE's useful multiplayer controls inside the existing game UI:
server filters, refresh and join; campaign/PvP hosting; campaign player limit,
friendly fire and extra enemies; direct connection where supported.

Use the existing widget and focus/event system so Quest laser selection,
A/back buttons, phone touch and gamepads reach the same actions. Keep the
existing campaign/profile menus, VR Settings injection and launcher entry
points. Reuse OpenCE's discovery and host configuration logic, with exact
network-version checks, rather than introducing another server directory.
Text entry must use the existing Android/VR input facilities or an accessible
in-game entry control; it must not require a physical keyboard.

The upstream XML menu loader, event handlers and required screens must be
reviewed together. Import only the dependency set required by these screens;
desktop display-mode and keyboard/mouse-only pages are outside this choice.
If the dependency boundary cannot preserve the existing controls, revise the
proposal before replacing working menus.

## Historical option B: full OpenCE menu replacement (selected)

Import the complete XML menu system and adapt campaign/profile/settings and
multiplayer screens for VR pointer, phone touch and gamepads. This exposes a
larger upstream feature set but touches saved-profile navigation, campaign
loading, text entry, desktop display settings and VR pause-menu injection.
It has a substantially larger device-validation scope.

## Checks and acceptance

Automated checks should exercise navigation, back/select, filters, exact
network rejection, host options, persisted settings and launch requests.
Compile both APK variants. Device acceptance must cover Quest pointer and
buttons, touch-only phone navigation, gamepad navigation, hosting/joining,
pause/VR Settings, profiles and single-player campaign entry. A build alone
does not establish that the screens are usable in a headset.
