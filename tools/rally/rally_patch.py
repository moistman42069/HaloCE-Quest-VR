"""Rally demo: adds a position dump to Halo CE Universal's source/game/players.c.

With HALO_POSITIONS set, the game then writes every player's machine and
position to d:\\positions.txt (positions.txt in the game data folder) every 3
ticks; system_link_bots_rally.py --gather steers its bots by it. Without
HALO_POSITIONS the game does exactly what it did before. The code is in the
port's HALO_LINUX part, so the Xbox build is untouched.

usage: python rally_patch.py <path of players.c>
"""

import sys

FUNCTION = """#ifdef HALO_LINUX /* rally demo (tools/rally/rally_patch.py): with HALO_POSITIONS set,
write every player's machine and position to d:\\positions.txt every 3 ticks */
static void demo_dump_player_positions(
\tvoid)
{
\tstatic unsigned long tick;
\tstruct data_iterator iterator;
\tstruct player_datum *player;
\tFILE *file;

\tif ((tick++ % 3) != 0 || !getenv("HALO_POSITIONS"))
\t\treturn;
\tfile = fopen("d:\\\\positions.txt", "wb");
\tif (!file)
\t\treturn;
\tdata_iterator_new(&iterator, player_data);
\twhile ((player = (struct player_datum *)data_iterator_next(&iterator)) != NULL)
\t{
\t\tif (player->unit_index != NONE)
\t\t{
\t\t\treal_point3d origin;

\t\t\tobject_get_origin(player->unit_index, &origin);
\t\t\tfprintf(file, "%d %f %f %f\\n",
\t\t\t\t(int)player->network_player_data.machine_index,
\t\t\t\torigin.x, origin.y, origin.z);
\t\t}
\t}
\tfprintf(file, "end\\n");
\tfclose(file);
}
#endif

"""

CALL = """#ifdef HALO_LINUX /* rally demo */
\tdemo_dump_player_positions();
#endif
"""

FUNCTION_ANCHOR = "void players_update_after_game(\n"
CALL_ANCHOR = "\tprofile_enter(PLAYERS_UPDATE_AFTER_GAME_PROFILE);\n"


def main():
    path = sys.argv[1]
    with open(path, "rb") as source:
        text = source.read().decode("latin-1")  # byte for byte
    if "demo_dump_player_positions" in text:
        print("players.c has the rally position dump already.")
        return 0
    newline = "\r\n" if "\r\n" in text else "\n"
    function_anchor = FUNCTION_ANCHOR.replace("\n", newline)
    call_anchor = CALL_ANCHOR.replace("\n", newline)
    if text.count(function_anchor) != 1 or text.count(call_anchor) != 1 or \
            text.index(call_anchor) < text.index(function_anchor):
        print("This players.c is different from the one the rally demo knows, so it was left alone.")
        return 1
    text = text.replace(call_anchor, CALL.replace("\n", newline) + call_anchor)
    text = text.replace(function_anchor, FUNCTION.replace("\n", newline) + function_anchor)
    with open(path, "wb") as source:
        source.write(text.encode("latin-1"))
    print("Added the rally position dump to players.c.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
