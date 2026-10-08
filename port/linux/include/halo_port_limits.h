/*
HALO_PORT_LIMITS.H

Multiplayer session limits of the native builds (Windows, Linux, Android),
force-included by halo_linux_prefix.h and halo_windows_prefix.h.

The Xbox game allows 16 players on at most 4 machines (up to 4 players each
on split screen). The native builds allow 128 players on up to 128
machines; split screen stays at 4 players per machine.

128 is the largest session that fits the game's existing records: player,
machine and team indices are stored in signed chars (0..127 with NONE), and
a finishing place in 7 bits.
*/

#ifndef __HALO_PORT_LIMITS_H
#define __HALO_PORT_LIMITS_H

/* ---------- session limits */

#define HALO_PORT_MAXIMUM_NETWORK_PLAYERS 128
#define HALO_PORT_MAXIMUM_NETWORK_MACHINES 128

/* a host polls its listening socket and one socket per machine; the Xbox's
Winsock headers default to 64 (the prefix headers define FD_SETSIZE from
this before any of them is read) */
#define HALO_PORT_FD_SETSIZE 256

/* ---------- memory capacity for these limits (game state and pools) */

#include "halo_port_capacity.h"

/* ---------- struct network_game layout

The game settings record (struct network_game) is declared separately in
several networking and interface units; its layout follows from the limits.
Every copy checks its offsets against these values. The Xbox values (4
machines, 16 players) are 0x226 and 0x434. */

#define HALO_PORT_NETWORK_MACHINE_SIZE 0x44
#define HALO_PORT_NETWORK_PLAYER_SIZE 0x20
#define HALO_PORT_NETWORK_GAME_MACHINES_OFFSET 0x114
#define HALO_PORT_NETWORK_GAME_PLAYER_COUNT_OFFSET \
	(HALO_PORT_NETWORK_GAME_MACHINES_OFFSET + HALO_PORT_MAXIMUM_NETWORK_MACHINES * HALO_PORT_NETWORK_MACHINE_SIZE)
#define HALO_PORT_NETWORK_GAME_PLAYERS_OFFSET (HALO_PORT_NETWORK_GAME_PLAYER_COUNT_OFFSET + 2)
#define HALO_PORT_NETWORK_GAME_PLAYERS_END \
	(HALO_PORT_NETWORK_GAME_PLAYERS_OFFSET + HALO_PORT_MAXIMUM_NETWORK_PLAYERS * HALO_PORT_NETWORK_PLAYER_SIZE)
#define HALO_PORT_NETWORK_GAME_RANDOM_SEED_OFFSET (HALO_PORT_NETWORK_GAME_PLAYERS_END + 2)
#define HALO_PORT_NETWORK_GAME_VARIANT_OPTIONS_OFFSET (HALO_PORT_NETWORK_GAME_PLAYERS_END + 0xA)
#define HALO_PORT_NETWORK_GAME_LEGACY_SIZE (HALO_PORT_NETWORK_GAME_PLAYERS_END + 0xE)
#define HALO_PORT_NETWORK_GAME_LOCAL_DATA_OFFSET (HALO_PORT_NETWORK_GAME_PLAYERS_END + 0x26)
#define HALO_PORT_NETWORK_GAME_SIZE (HALO_PORT_NETWORK_GAME_PLAYERS_END + 0x2A)

/* ---------- system link protocol

The native builds' messages differ from the Xbox game's (longer arrays, the
game settings record in fragments), so they search for games with their own
protocol version and never see the Xbox game's, or it theirs. */

#define HALO_PORT_NETWORK_GAME_MESSAGE_VERSION 2

/* The native builds' network code uses an unsigned 16-bit host version in
game advertisements. This build advertises 24; supported PvP clients may
accept a compatible host version from the declared range. Hosts built before
the field was added send zero, which clients reject. Raise the host version
when a wire change requires it. */
/* This build hosts and advertises as OpenCE network version 24. The supported
PvP host range (11..24) follows ChupaThingyCE's OpenCE-derived compatibility
table; client selection can narrow discovery/admission but never changes the
local wire version. Campaign and Custom Edition map joins require version 23
or newer. The range is also consumed by Android launcher/update metadata. */
#define HALO_PORT_NETWORK_VERSION 24
#define HALO_PORT_NETWORK_VERSION_MINIMUM 11
#define HALO_PORT_NETWORK_VERSION_MAXIMUM 24
#define HALO_PORT_CAMPAIGN_NETWORK_VERSION_MINIMUM 23
#define HALO_PORT_CUSTOM_EDITION_NETWORK_VERSION_MINIMUM 23
/* The binary always hosts/advertises as 24. This immutable startup selection
 * controls which compatible remote PvP protocol versions are listed/joined;
 * zero means all compatible versions in the declared 11..24 range. */
int halo_port_active_network_version(void);
/* ... the advertisement's reserved bytes: the version (a little-endian word),
then flags */
#define HALO_PORT_ADVERTISED_VERSION_OFFSET 0
#define HALO_PORT_ADVERTISED_FLAGS_OFFSET 2
/* ... the host plays the distributed netcode (always, since the lockstep
netcode was removed; hosts of version 4 built before then may not) */
#define HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG 0x01
/* ... the game is under way (loading, playing or over), not in its lobby:
the menus show it before joining it (hosts built before then never set it) */
#define HALO_PORT_ADVERTISED_IN_PROGRESS_FLAG 0x02

/* a message header's 12-bit length allows messages of up to 0xFFF bytes,
header included; the per-tick update of 128 players is 3,857 */
#define HALO_PORT_MAXIMUM_NETWORK_MESSAGE_SIZE 0x1000

/* the packet codec's limit on a decoded or encoded packet; the per-tick
update of 128 players decodes to 0x1010 bytes */
#define HALO_PORT_NETWORK_PACKET_SIZE 0x1100

/* the game settings record (HALO_PORT_NETWORK_GAME_SIZE, 13,120 bytes at 128
machines and players) does not fit one message; it is sent in pieces of
this many bytes (4 pieces), each 3,594 bytes on the wire */
#define HALO_PORT_NETWORK_GAME_SETTINGS_FRAGMENT_SIZE 0xE00

#endif /* __HALO_PORT_LIMITS_H */
