"""Rally boarding demo: adds a vehicle and seat dump to Halo CE Universal's source/game/players.c.

With HALO_POSITIONS set, the game then also writes d:\\vehicles.txt (vehicles.txt
in the game data folder) every 3 ticks: every vehicle's position and tag
name, the entrance point of each of its seats with whether a player could
take it, and which machines' players are seated in something.
system_link_bots_board.py --board steers its bots by it, to the nearest
Pelican or Phantom and in. It sits beside rally_patch.py's position dump
(apply both; either order), and like it is in the port's HALO_LINUX part, so
the Xbox build is untouched. Without HALO_POSITIONS the game does exactly
what it did before.

usage: python rally_board_patch.py <path of players.c>
"""

import sys

FUNCTION = """#ifdef HALO_LINUX /* rally boarding demo (tools/rally/rally_board_patch.py): with HALO_POSITIONS
set, write every vehicle, the entrance point of each of its seats and the seated players to
d:\\\\vehicles.txt every 3 ticks */
/* units.c's, which no header declares */
boolean unit_get_seat_entrance_point(long unit_index, long target_unit_index, short seat_index,
\treal_point3d *entry_position, real_point3d *exit_position, real_point3d *seat_transform);
/* tag_files.h's */
char *tag_get_name(long tag_index);

static void demo_dump_vehicles(
\tvoid)
{
\t/* (units.c's _unit_seat_requires_driver_bit) */
\tenum { seat_requires_driver_bit = 9 };
\tstatic unsigned long tick;
\tstruct data_iterator players;
\tstruct object_iterator vehicles;
\tstruct player_datum *player;
\tlong probe_unit_index = NONE;
\tFILE *file;

\tif ((tick++ % 3) != 0 || !getenv("HALO_POSITIONS"))
\t\treturn;
\tfile = fopen("d:\\\\vehicles.txt", "wb");
\tif (!file)
\t\treturn;
\t/* who is seated, and a player on foot to ask the seats' entrance points
\tfor (the multiplayer bipeds all enter the same way) */
\tdata_iterator_new(&players, player_data);
\twhile ((player = (struct player_datum *)data_iterator_next(&players)) != NULL)
\t{
\t\tif (player->unit_index == NONE)
\t\t\tcontinue;
\t\tif (unit_get(player->unit_index)->object.parent_object_index != NONE)
\t\t\tfprintf(file, "seated %d\\n", (int)player->network_player_data.machine_index);
\t\telse if (probe_unit_index == NONE)
\t\t\tprobe_unit_index = player->unit_index;
\t}
\tobject_iterator_new(&vehicles, _object_mask_vehicle, 0);
\twhile (object_iterator_next(&vehicles))
\t{
\t\tstruct unit_datum *vehicle = unit_get(vehicles.index);
\t\tstruct unit_definition *definition = unit_definition_get(vehicle->definition_index);
\t\treal_point3d origin;
\t\tshort seat_index;

\t\tobject_get_origin(vehicles.index, &origin);
\t\tfprintf(file, "vehicle %ld %f %f %f %s\\n", vehicles.index, origin.x, origin.y, origin.z,
\t\t\ttag_get_name(vehicle->definition_index));
\t\tif (probe_unit_index == NONE)
\t\t\tcontinue;
\t\tfor (seat_index = 0; seat_index < definition->unit.seats.count; seat_index++)
\t\t{
\t\t\tstruct unit_seat *seat = TAG_BLOCK_GET_ELEMENT(&definition->unit.seats, seat_index, struct unit_seat);
\t\t\treal_point3d entrance;
\t\t\treal_point3d seat_position;
\t\t\tlong occupant_unit_index = NONE;
\t\t\tboolean free;
\t\t\tboolean needs_driver;

\t\t\tif (!unit_get_seat_entrance_point(probe_unit_index, vehicles.index, seat_index, &entrance,
\t\t\t\t&seat_position, NULL))
\t\t\t{
\t\t\t\tcontinue;
\t\t\t}
\t\t\tfree = unit_can_enter_seat(probe_unit_index, vehicles.index, seat_index, &occupant_unit_index);
\t\t\tneeds_driver = TEST_FLAG(seat->flags, seat_requires_driver_bit) &&
\t\t\t\tvehicle->unit.driver_object_index == NONE;
\t\t\t/* seat <vehicle> <seat> <entrance x y z> <free> <driver seat> <waits for a driver> <seat x y z> */
\t\t\tfprintf(file, "seat %ld %d %f %f %f %d %d %d %f %f %f\\n", vehicles.index, seat_index,
\t\t\t\tentrance.x, entrance.y, entrance.z, free ? 1 : 0,
\t\t\t\tTEST_FLAG(seat->flags, _unit_seat_driver_bit) ? 1 : 0, needs_driver ? 1 : 0,
\t\t\t\tseat_position.x, seat_position.y, seat_position.z);
\t\t}
\t}
\tfprintf(file, "end\\n");
\tfclose(file);
}
#endif

"""

CALL = """#ifdef HALO_LINUX /* rally boarding demo */
\tdemo_dump_vehicles();
#endif
"""

FUNCTION_ANCHOR = "void players_update_after_game(\n"
CALL_ANCHOR = "\tprofile_enter(PLAYERS_UPDATE_AFTER_GAME_PROFILE);\n"


def main():
    path = sys.argv[1]
    with open(path, "rb") as source:
        text = source.read().decode("latin-1")  # byte for byte
    if "demo_dump_vehicles" in text:
        print("players.c has the rally vehicle dump already.")
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
    print("Added the rally vehicle dump to players.c.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
