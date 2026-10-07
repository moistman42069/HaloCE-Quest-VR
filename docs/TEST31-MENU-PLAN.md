# Test31 in-game menu proposal

Status: awaiting the owner's menu-scope decision. No menu implementation yet.

## Recommended: browser and Server Setup first

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

## Alternative: full OpenCE menu replacement

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
