# Rally demo

Bots join your system link game and run to where you stand: up to 127
of them, a game of 128 players on one PC. For a PC where
[HaloLauncher.exe](https://github.com/bnunu/halo-ce-universal/releases/latest)
installed Halo CE Universal.

In a Command Prompt:

```bat
curl.exe -fsSL -o "%TEMP%\rally.cmd" https://raw.githubusercontent.com/bnunu/halo-ce-universal/main/tools/rally/rally.cmd && "%TEMP%\rally.cmd" 127
```

`rally.cmd` starts Halo. Create a system link game (Multiplayer), wait in
the lobby, then press a key in the rally window: the bots join, the game
starts, and about 3 seconds in they run to where you are standing. Ctrl+C in
the rally window takes them out. Give it another number for fewer bots.

For another round, run the same command again while Halo is running, in a
lobby or in a game: it sees Halo and only brings in the bots. The bots need
the game to write their positions: a game built with the position dump
(which a Halo update takes out again) and started with `HALO_POSITIONS`,
which the rally also saves in the launcher's settings, so that Halo started
from the launcher or its shortcut has it too. With Halo running, the rally
goes ahead when the game has written positions in the last few seconds or
was built with the dump, and asks you to close Halo and run it again only
when an update took the dump out.

The first time (and after every update of the game), `rally.cmd` adds a
position dump to the installed game's `source/game/players.c`
(`rally_patch.py`) and rebuilds it, which takes a minute or two. With
`HALO_POSITIONS` set, which only `rally.cmd` sets, the game writes every
player's position to `positions.txt` in its data folder every 3 ticks; the
bots (`system_link_bots_rally.py`, `tools/system_link_bots.py` with
`--wander`, `--positions` and `--gather`) steer by it. The dump is in the
port's `HALO_LINUX` code, so the Xbox build is untouched.

The bots are stand-ins that speak the system link protocol and only run,
jump and turn: they don't fight.

## Boarding

A variant, run by hand: the bots board the map's dropships.
`rally_board_patch.py` adds a second dump beside the position dump: every
vehicle, the entrance of each of its seats and who sits where, in
`vehicles.txt` in the data folder. `system_link_bots_board.py`, a copy of
the rally bots, then sends each bot with `--board` to the nearest free
passenger seat of a Pelican or Phantom and in (a Phantom's bay with a
jump). The game gives no seat in a vehicle that holds an enemy, so this
takes a team game with players on both teams, which `--team split` sets up
from the lobby:

```bat
python tools\rally\rally_patch.py source\game\players.c
python tools\rally\rally_board_patch.py source\game\players.c
ninja windows
rem start the host: HALO_POSITIONS=1, HALO_NETCODE=lockstep and
rem HALO_NETWORK_TEST=host:<map>:team_slayer, on a map with dropships
python tools\rally\system_link_bots_board.py --machines 127 --start --team split --board ^
  --positions <data>\positions.txt --vehicles <data>\vehicles.txt
```

The scripts' own descriptions give the details: how close a seat has to
be, driver seats (left alone unless `--board-drivers`: a dropship with a
driver lifts off), and how teams are chosen.
