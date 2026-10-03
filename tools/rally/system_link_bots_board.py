"""Stand-in system link machines for testing large multiplayer sessions.

Joins a native-build Halo host (port/, built with HALO_LINUX) with many
lightweight machines, each with one player, speaking the game's system link
protocol directly: TCP to the host's port 5150 for the game's messages, UDP for
player input. Each machine binds its own loopback address (127.0.0.2,
127.0.0.3, ...) because the host tells machines apart by address, so run it on
the host's computer (or give it --first-address on a network where the
addresses are yours).

    python tools/system_link_bots.py --machines 127 --start

joins 127 machines to the host at 127.0.0.1, marks the map precached, asks
the host to start once everyone is in, then plays: every machine
acknowledges each tick's update and sends its player's input (standing
still and slowly turning, or with --wander running about, which keeps the
spawn points clear), the way a real client keeps a lockstep game running. The bots do not simulate the game; they only keep up with the
host's update stream. Ctrl+C leaves.

The protocol (network_messages.c): a message is a 2-byte big-endian header
(length << 4 | type << 2, length including the header), then a packet: a
version byte, the fields big-endian (bytes and raw fields as they are), and
the packet type in a trailing byte. The native builds send the game settings
record in pieces of HALO_PORT_NETWORK_GAME_SETTINGS_FRAGMENT_SIZE bytes.

Boarding (demo; this copy of system_link_bots_rally.py adds it): with
--board, --positions and --vehicles, every machine's player runs to the
entrance of the nearest free seat of a vehicle whose tag name has one of the
--board words in it (Pelicans and Phantoms by default), stops on it and
holds the action button until the host's dump shows it seated, then sits
still. Driver seats are left alone unless --board-drivers: a dropship with a
driver lifts off, and its other seats with it. The game offers a seat only
to a player within a world unit of the seat's entrance or of the seat itself
(unit_find_nearby_seat), so the players make for the nearer of the two, slow
down on the last units, and press the action button once there or once
stuck close by, jumping when the seat is above reach (a Phantom's bay: the
player is still at the top of a standing jump); a seat that does not take in
a few seconds is left for another. With every seat taken, the rest stand by the nearest such
vehicle.

Teams (demo): --team host (or a team number) asks the host, from the lobby,
to put every machine's player on the host player's team, as the lobby's team
choice does (a player settings request); --team split puts every other one
there and the rest on the other team (red and blue), since a team game
starts only with players on both. The start waits until they all are.
The game refuses a seat in a vehicle that holds an enemy
(unit_can_enter_seat), so boarding shared dropships needs a team game
(host with debug.network_test "host:<map>:team_slayer") and one team.
With teams, a seat counts as taken when a seated player is on it, and a
vehicle as open to a player when no one of another team sits in it (the
dump's own free flag answers for one player only). The host writes the dump when
built with tools/rally/rally_board_patch.py (vehicles.txt) and
rally_patch.py (positions.txt) and started with HALO_POSITIONS.
"""

import argparse
import errno
import ipaddress
import math
import random
import selectors
import socket
import struct
import sys
import time

SERVER_PORT = 0x141E
CLIENT_PORT = 0x141F
MESSAGE_TYPE_PACKET = 3
PACKET_VERSION = 1
JOIN_TOKEN = b"message in a bottle"[:16]  # network_game_generate_join_game_token (DEBUG builds)
SETTINGS_FRAGMENT_SIZE = 0xE00
NONE = -1

# network_game_message_type
CLIENT_BROADCAST_GAME_SEARCH = 0
SERVER_GAME_ADVERTISE = 2
SERVER_MACHINE_ACCEPTED = 4
SERVER_MACHINE_REJECTED = 5
SERVER_GAME_SETTINGS_UPDATE = 6
SERVER_PREGAME_COUNTDOWN = 7
SERVER_BEGIN_GAME = 8
SERVER_GRACEFUL_GAME_EXIT_PREGAME = 9
SERVER_PREGAME_KEEP_ALIVE = 10
SERVER_POSTGAME_KEEP_ALIVE = 11
CLIENT_JOIN_GAME_REQUEST = 12
CLIENT_ADD_PLAYER_REQUEST_PREGAME = 13
CLIENT_SETTINGS_REQUEST = 15
CLIENT_PLAYER_SETTINGS_REQUEST = 16
CLIENT_GAME_START_REQUEST = 17
CLIENT_MAP_IS_PRECACHED_PREGAME = 19
SERVER_GAME_UPDATE = 20
SERVER_ADD_PLAYER_INGAME = 21
SERVER_REMOVE_PLAYER_INGAME = 22
SERVER_GAME_OVER = 23
CLIENT_LOADED = 24
CLIENT_GAME_UPDATE = 25
SERVER_SWITCH_TO_PREGAME = 30
SERVER_GRACEFUL_GAME_EXIT_POSTGAME = 31

COUNTDOWN_EVENT_START_IMMEDIATELY = 3

MESSAGE_NAMES = {
    SERVER_GAME_ADVERTISE: "advertise", SERVER_MACHINE_ACCEPTED: "machine_accepted",
    SERVER_MACHINE_REJECTED: "machine_rejected", SERVER_GAME_SETTINGS_UPDATE: "settings",
    SERVER_PREGAME_COUNTDOWN: "countdown", SERVER_BEGIN_GAME: "begin_game",
    SERVER_GRACEFUL_GAME_EXIT_PREGAME: "exit_pregame", SERVER_PREGAME_KEEP_ALIVE: "keep_alive",
    SERVER_POSTGAME_KEEP_ALIVE: "postgame_keep_alive", SERVER_GAME_UPDATE: "game_update",
    SERVER_ADD_PLAYER_INGAME: "add_player_ingame", SERVER_REMOVE_PLAYER_INGAME: "remove_player_ingame",
    SERVER_GAME_OVER: "game_over", SERVER_SWITCH_TO_PREGAME: "switch_to_pregame",
    SERVER_GRACEFUL_GAME_EXIT_POSTGAME: "exit_postgame",
}


def network_game_layout(machines, players):
    """Offsets of struct network_game (port/linux/include/halo_port_limits.h)."""
    player_count = 0x114 + machines * 0x44
    players_offset = player_count + 2
    size = players_offset + players * 0x20 + 0xE
    return {"map_name": 0x24, "machine_count": 0x112, "player_count": player_count,
            "players": players_offset, "size": size}


def wide(text, count):
    units = [ord(c) for c in text[:count - 1]]
    units += [0] * (count - len(units))
    return struct.pack(">%dH" % count, *units)


def message(packet_type, payload):
    packet = bytes([PACKET_VERSION]) + payload + bytes([packet_type])
    length = len(packet) + 2
    assert length <= 0xFFF, "message too long for its header"
    return struct.pack(">H", (length << 4) | (MESSAGE_TYPE_PACKET << 2)) + packet


def network_player(name, machine_index, color, team=NONE, list_index=NONE):
    # shorts 12 (name), shorts 2 (colour, icon), bytes 4 (machine, controller, team, list index)
    return (wide(name, 12) + struct.pack(">hh", color, 0) +
            struct.pack("bbbb", machine_index, 0, team, list_index))


def lobby_players(settings):
    """The players of a game settings record (struct network_game, as the
    host keeps it): (machine, controller, team, list index) of each."""
    for machine_slots in (128, 4):
        layout = network_game_layout(machine_slots, 128 if machine_slots == 128 else 16)
        if len(settings) == layout["size"]:
            count = struct.unpack_from("<h", settings, layout["player_count"])[0]
            players = []
            for index in range(max(0, count)):
                entry = layout["players"] + index * 0x20
                players.append(struct.unpack_from("bbbb", settings, entry + 0x1C))
            return players
    return []


UNIT_CONTROL_JUMP = 1 << 1  # _unit_control_jump_bit
UNIT_CONTROL_ACTION = 1 << 6  # _unit_control_action_bit


def player_action(yaw, forward=0.0, control_flags=0):
    # longs 6 (unit control flags, desired facing yaw and pitch, throttle i
    # (forward) and j (strafe), primary trigger), shorts 3 (weapon, grenade,
    # zoom level); the pad is not sent
    return (struct.pack(">Ifffff", control_flags, yaw, 0.0, forward, 0.0, 0.0) +
            struct.pack(">hhh", 0, 0, NONE))


class Machine:
    def __init__(self, index, address, host, log):
        self.index = index
        self.address = address
        self.host = host
        self.log = log
        self.name = "bot%d" % index
        self.state = "connecting"
        self.machine_index = None
        self.buffer = b""
        self.settings = bytearray()
        self.settings_complete = None
        self.map_name = None
        self.last_update_number = None
        self.updates_received = 0
        self.bytes_received = 0
        self.last_precache_time = 0
        self.player_added = False
        self.player_list_index = None
        # teams (demo): the team this machine's player should be on (None: any)
        self.wanted_team = None
        self.team_host = False
        self.team_split = False
        self.team_index = None
        self.last_team_request = 0
        self.connect_attempts = 0
        self.retry_time = 0
        self.load_seconds = 1.0
        self.wander = False
        # gathering (demo): steered from the host's position dump
        self.gather = None  # shared state: {"target": (x, y) or None, "positions": {...}, "radius": r}
        self.stopped = False
        self.history = []  # (time, x, y)
        self.detour_until = 0
        self.detour_yaw = 0.0
        self.next_jump = 0
        self.rng = random.Random(index)
        self.gather_yaw = self.index * 2.3999632 % (2 * math.pi)
        # boarding (demo): steered from the host's vehicle and seat dump
        self.board = None  # shared state: {"positions", "vehicles", "seats", "seated", "claims", "words"}
        self.board_seat = None  # (vehicle, seat) this player is making for
        self.board_repick = 0
        self.board_skipped = {}  # (vehicle, seat) -> time it may be tried again
        self.board_still_since = None
        self.board_at_seat_since = None
        self.board_near_since = None
        self.tcp = None
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # the host's own client holds 0.0.0.0 on this port (with SO_REUSEADDR);
        # Linux lets another socket bind a single address on it only if it
        # sets SO_REUSEADDR too
        self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp.bind((address, CLIENT_PORT))
        self.udp.setblocking(False)

    def connect(self):
        self.connect_attempts += 1
        self.state = "connecting"
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 20)
        self.tcp.bind((self.address, 0))
        self.tcp.setblocking(False)
        try:
            self.tcp.connect((self.host, SERVER_PORT))
        except BlockingIOError:
            pass
        except OSError as error:
            # a non-blocking connect in progress (Windows says would block)
            if error.errno not in (errno.EINPROGRESS, errno.EWOULDBLOCK, 10035):
                raise

    def close(self, selector):
        """stops using the connection: a connection the host keeps but no one
        reads would fill its send buffer"""
        self.state = "closed"
        if self.tcp:
            try:
                selector.unregister(self.tcp)
            except (KeyError, ValueError):
                pass
            self.tcp.close()
            self.tcp = None

    def send(self, data):
        view = memoryview(data)
        deadline = time.monotonic() + 5
        while view:
            try:
                sent = self.tcp.send(view)
                view = view[sent:]
            except BlockingIOError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.001)

    def joined(self):
        self.send(message(CLIENT_JOIN_GAME_REQUEST, wide(self.name, 32) + JOIN_TOKEN))
        self.state = "joining"

    def receive(self):
        try:
            data = self.tcp.recv(1 << 20)
        except BlockingIOError:
            return True
        except ConnectionError:
            self.log("%s: connection lost" % self.name)
            self.state = "closed"
            return False
        if not data:
            self.log("%s: host closed the connection" % self.name)
            self.state = "closed"
            return False
        self.bytes_received += len(data)
        self.buffer += data
        while len(self.buffer) >= 2:
            header = struct.unpack(">H", self.buffer[:2])[0]
            length = header >> 4
            if length < 3:
                self.log("%s: bad message header %04x" % (self.name, header))
                self.state = "closed"
                return False
            if len(self.buffer) < length:
                break
            packet = self.buffer[2:length]
            self.buffer = self.buffer[length:]
            self.handle(packet[-1], packet[1:-1])
        return True

    def handle(self, packet_type, payload):
        if packet_type == SERVER_MACHINE_ACCEPTED:
            random_seed, self.machine_index = struct.unpack(">ih", payload[:6])
            self.state = "pregame"
            self.send(message(CLIENT_SETTINGS_REQUEST, wide(self.name, 32) + bytes([self.machine_index & 0xFF])))
        elif packet_type == SERVER_MACHINE_REJECTED:
            self.log("%s: rejected, reason %d" % (self.name, struct.unpack(">h", payload[:2])[0]))
            self.state = "rejected"
        elif packet_type == SERVER_GAME_SETTINGS_UPDATE:
            total, offset, length = struct.unpack(">HHH", payload[:6])
            data = payload[6:6 + length]
            if offset == 0:
                self.settings = bytearray()
            if offset == len(self.settings):
                self.settings += data
            if len(self.settings) == total:
                self.settings_complete = bytes(self.settings)
                self.map_name = self.settings_complete[0x24:0x24 + 0x80].split(b"\0")[0]
                for machine, controller, team, list_index in lobby_players(self.settings_complete):
                    if machine == self.machine_index and controller == 0:
                        self.team_index, self.player_list_index = team, list_index
                    if machine == 0 and controller == 0 and self.team_host:
                        # (split: the other of red and blue for every other machine)
                        self.wanted_team = team if not self.team_split or self.index % 2 == 0 else 1 - team
                if not self.player_added and self.machine_index is not None:
                    self.player_added = True
                    color = self.index % 18
                    self.send(message(CLIENT_ADD_PLAYER_REQUEST_PREGAME,
                                      network_player(self.name, self.machine_index, color)))
        elif packet_type == SERVER_BEGIN_GAME:
            self.state = "loading"
            self.loaded_at = time.monotonic() + self.load_seconds
        elif packet_type == SERVER_GAME_UPDATE:
            update_number = struct.unpack(">I", payload[:4])[0]
            self.last_update_number = update_number
            self.updates_received += 1
            if self.state != "ingame":
                self.state = "ingame"
        elif packet_type in (SERVER_GAME_OVER,):
            self.state = "postgame"
        elif packet_type in (SERVER_SWITCH_TO_PREGAME,):
            self.state = "pregame"
            self.last_update_number = None
            self.player_added = True
        elif packet_type in (SERVER_GRACEFUL_GAME_EXIT_PREGAME, SERVER_GRACEFUL_GAME_EXIT_POSTGAME):
            self.log("%s: host ended the game" % self.name)
            self.state = "closed"

    def gather_steer(self, now):
        """Heading, throttle and control flags towards the gathering point:
        run there and stop within the radius (or where the crowd packs in
        close by); when something stops the way further out, run off at a
        random angle for a few seconds, jumping, and try again."""
        target = self.gather.get("target")
        position = self.gather["positions"].get(self.machine_index)
        if target is None or position is None:
            return self.gather_yaw, 0.0, 0
        x, y = position[0], position[1]
        dx, dy = target[0] - x, target[1] - y
        distance = math.hypot(dx, dy)
        radius = self.gather["radius"]
        self.gather_yaw = math.atan2(dy, dx) % (2 * math.pi)
        if self.stopped:
            if distance > radius * 6:
                self.stopped = False  # respawned elsewhere: go back
                self.history = []
            else:
                return self.gather_yaw, 0.0, 0
        self.history.append((now, x, y))
        while self.history and now - self.history[0][0] > 1.5:
            self.history.pop(0)
        moved = math.hypot(x - self.history[0][1], y - self.history[0][2]) if self.history else 0.0
        waited = now - self.history[0][0] if self.history else 0.0
        if distance < radius:
            self.stopped = True
            return self.gather_yaw, 0.0, 0
        if now >= self.detour_until and waited > 1.0 and moved < 0.3:
            if distance < radius * 3:
                self.stopped = True  # packed in by the crowd
                return self.gather_yaw, 0.0, 0
            # blocked: run off at a random angle for a while, then try again
            side = self.rng.choice((-1, 1))
            self.detour_yaw = (self.gather_yaw + side * self.rng.uniform(1.0, 2.6)) % (2 * math.pi)
            self.detour_until = now + self.rng.uniform(1.5, 4.0)
            self.next_jump = now
            self.history = []
        if now < self.detour_until:
            flags = 0
            if now >= self.next_jump:
                flags = UNIT_CONTROL_JUMP
                self.next_jump = now + 1.0
            return self.detour_yaw, 1.0, flags
        return self.gather_yaw, 1.0, 0

    def board_claim(self, seat):
        claims = self.board["claims"]
        if self.board_seat is not None:
            claims[self.board_seat] = max(0, claims.get(self.board_seat, 1) - 1)
        self.board_seat = seat
        if seat is not None:
            claims[seat] = claims.get(seat, 0) + 1
        self.board_at_seat_since = None
        self.board_still_since = None
        self.board_near_since = None

    def board_seat_open(self, key, seat):
        """Whether this machine's player may take the seat: a passenger seat
        (or any with --board-drivers) not waiting for a driver, which no one
        sits on, in a vehicle where no one of another team sits."""
        board = self.board
        if seat["waits"] or (seat["driver"] and not board["drivers"]) or key in board["taken"]:
            return False
        if not board["teams"]:
            return seat["free"]
        teams = board["vehicle_teams"].get(key[0], set())
        return not teams or teams == {self.team_index}

    def board_run(self, now, x, y, target_x, target_y, stop_radius):
        """Heading and throttle towards a point, with gather_steer's way
        round an obstacle; None once within stop_radius."""
        dx, dy = target_x - x, target_y - y
        distance = math.hypot(dx, dy)
        self.gather_yaw = math.atan2(dy, dx) % (2 * math.pi)
        if distance < stop_radius:
            return None
        self.history.append((now, x, y))
        while self.history and now - self.history[0][0] > 1.5:
            self.history.pop(0)
        moved = math.hypot(x - self.history[0][1], y - self.history[0][2]) if self.history else 0.0
        waited = now - self.history[0][0] if self.history else 0.0
        if now >= self.detour_until and waited > 1.0 and moved < 0.3 and distance > 2.0:
            side = self.rng.choice((-1, 1))
            self.detour_yaw = (self.gather_yaw + side * self.rng.uniform(1.0, 2.6)) % (2 * math.pi)
            self.detour_until = now + self.rng.uniform(1.0, 2.5)
            self.next_jump = now
            self.history = []
        if now < self.detour_until:
            flags = 0
            if now >= self.next_jump:
                flags = UNIT_CONTROL_JUMP
                self.next_jump = now + 1.0
            return self.detour_yaw, 1.0, flags
        # the last units slowly, not to run past the entrance
        return self.gather_yaw, 1.0 if distance > 2.0 else 0.3, 0

    def board_steer(self, now):
        """Heading, throttle and control flags for boarding: to the entrance
        of the nearest free seat, stop there and hold the action button once
        standing still; sit still when seated; stand by the nearest vehicle
        when no seat is free."""
        board = self.board
        position = board["positions"].get(self.machine_index)
        if position is None:
            return self.gather_yaw, 0.0, 0
        x, y, z = position
        if self.machine_index in board["seated"]:
            if self.board_seat is not None:
                self.board_claim(None)
            return self.gather_yaw, 0.0, 0
        seats = board["seats"]
        current = seats.get(self.board_seat) if self.board_seat is not None else None
        if self.board_seat is not None and (current is None or not self.board_seat_open(self.board_seat, current)):
            self.board_claim(None)
        if self.board_seat is None or now >= self.board_repick:
            self.board_repick = now + 2.0
            best, best_score = None, None
            for key, seat in seats.items():
                if not self.board_seat_open(key, seat) or self.board_skipped.get(key, 0) > now:
                    continue
                distance = min(math.dist((x, y, z), seat["entrance"]), math.dist((x, y, z), seat["seat"]))
                claims = board["claims"].get(key, 0) - (1 if key == self.board_seat else 0)
                score = distance + 4.0 * claims
                if best_score is None or score < best_score:
                    best, best_score = key, score
            if best != self.board_seat:
                self.board_claim(best)
        if self.board_seat is None:
            # every seat taken: stand by the nearest vehicle
            vehicles = board["vehicles"]
            if not vehicles:
                return self.gather_yaw, 0.0, 0
            vx, vy, _ = min(vehicles.values(), key=lambda v: math.dist((x, y, z), v))
            steer = self.board_run(now, x, y, vx, vy, 6.0)
            return steer if steer else (self.gather_yaw, 0.0, 0)
        seat = seats[self.board_seat]
        ex, ey, ez = min((seat["entrance"], seat["seat"]), key=lambda point: math.dist((x, y, z), point))
        # (a standing player's middle is about half a unit over its feet, and the
        # game wants that within a unit of the point)
        above_reach = ez - z > 1.4
        near = math.hypot(ex - x, ey - y) < 1.5
        if near and self.board_near_since is None:
            self.board_near_since = now
        elif not near:
            self.board_near_since = None
        steer = self.board_run(now, x, y, ex, ey, 0.4)
        stuck_close = (near and now - self.board_near_since > 1.5 and len(self.history) > 1 and
                       math.hypot(x - self.history[0][1], y - self.history[0][2]) < 0.15)
        if steer and not stuck_close:
            self.board_at_seat_since = None
            self.board_still_since = None
            return steer
        # on the entrance: wait to stand still, then hold the action button
        if self.board_at_seat_since is None:
            self.board_at_seat_since = now
            self.board_still_since = None
            self.board_last = (x, y)
        if math.hypot(x - self.board_last[0], y - self.board_last[1]) < 0.02:
            if self.board_still_since is None:
                self.board_still_since = now
        else:
            self.board_still_since = None
        self.board_last = (x, y)
        if now - self.board_at_seat_since > (6.0 if above_reach else 3.0):
            # the seat did not take (out of reach, or someone else's): another
            self.board_skipped[self.board_seat] = now + 20.0
            self.board_claim(None)
            return self.gather_yaw, 0.0, 0
        if above_reach:
            # jump now and then, holding the action button throughout: the
            # seat is offered at the top of the jump
            flags = UNIT_CONTROL_ACTION
            if now >= self.next_jump:
                flags |= UNIT_CONTROL_JUMP
                self.next_jump = now + 1.2
            return self.gather_yaw, 0.0, flags
        if self.board_still_since is not None and now - self.board_still_since >= 0.2:
            return self.gather_yaw, 0.0, UNIT_CONTROL_ACTION
        return self.gather_yaw, 0.0, 0

    def team_ready(self):
        return self.wanted_team is None or self.team_index == self.wanted_team

    def tick(self, now):
        if (self.state == "pregame" and self.wanted_team is not None and self.player_list_index is not None and
                self.player_list_index >= 0 and not self.team_ready() and now - self.last_team_request > 1.0):
            self.last_team_request = now
            self.send(message(CLIENT_PLAYER_SETTINGS_REQUEST,
                              network_player(self.name, self.machine_index, self.index % 18,
                                             self.wanted_team, self.player_list_index)))
        if self.state == "pregame" and self.map_name and now - self.last_precache_time > 1.0:
            self.last_precache_time = now
            self.send(message(CLIENT_MAP_IS_PRECACHED_PREGAME, self.map_name.ljust(256, b"\0")[:256]))
        if self.state == "loading" and now >= self.loaded_at:
            self.send(message(CLIENT_LOADED, struct.pack(">i", 0)))
            self.state = "loaded"
        if self.state == "ingame" and self.last_update_number is not None:
            # the next update this machine expects (acknowledging the ones it
            # has), then an array of its players' actions: a count byte and one
            # action
            flags = 0
            if self.gather is not None:
                yaw, forward, flags = self.gather_steer(now)
            elif self.board is not None:
                yaw, forward, flags = self.board_steer(now)
            elif self.wander:
                # run on a heading of its own (golden-angle spread), weaving a
                # little, so the spawn points clear as they would in a real game
                yaw = (self.index * 2.3999632 + 0.4 * math.sin(now * 0.3 + self.index)) % (2 * math.pi)
                forward = 1.0
            else:
                yaw = (now * 0.5 + self.index) % (2 * math.pi)
                forward = 0.0
            payload = (struct.pack(">I", (self.last_update_number + 1) & 0x7FFFFFFF) + bytes([1]) +
                       player_action(yaw, forward, flags))
            try:
                self.udp.sendto(message(CLIENT_GAME_UPDATE, payload), (self.host, SERVER_PORT))
            except OSError:
                pass


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--machines", type=int, default=8)
    parser.add_argument("--first-address", default="127.0.0.2",
                        help="each machine binds this address plus its number")
    parser.add_argument("--start", action="store_true",
                        help="ask the host to start as soon as every machine has a player")
    parser.add_argument("--start-delay", type=float, default=3.0)
    parser.add_argument("--seconds", type=float, default=0, help="leave after this long (0: until Ctrl+C)")
    parser.add_argument("--rate", type=float, default=30.0, help="input messages per second per machine")
    parser.add_argument("--join-rate", type=float, default=20.0, help="machines connecting per second")
    parser.add_argument("--load-seconds", type=float, default=1.0,
                        help="how long each machine takes to load the map once the game begins")
    parser.add_argument("--wander", action="store_true",
                        help="players run about instead of standing still; a standing player "
                             "blocks its spawn point (no one spawns within 2 world units of an enemy)")
    parser.add_argument("--status-every", type=float, default=5.0)
    parser.add_argument("--positions", help="(demo) the host's player position dump to steer by")
    parser.add_argument("--gather", default=None,
                        help="(demo, with --positions) run to one spot and stop there: 'machine:N' "
                             "(where that machine's player stands once the game is under way) or 'x,y'")
    parser.add_argument("--gather-radius", type=float, default=2.5)
    parser.add_argument("--board", nargs="?", const="pelican,phantom", default=None,
                        help="(demo, with --positions and --vehicles) board the vehicles whose tag names "
                             "have one of these comma-separated words (default: pelican,phantom)")
    parser.add_argument("--vehicles", help="(demo) the host's vehicle and seat dump to board by")
    parser.add_argument("--team", default=None,
                        help="(demo) put every machine's player on this team in the lobby: a number, "
                             "'host' for the host player's (for a team game's shared vehicles), or "
                             "'split' for half on the host player's team and half on the other")
    parser.add_argument("--board-drivers", action="store_true",
                        help="(demo) take driver seats too (a dropship with a driver lifts off)")
    options = parser.parse_args()

    started = time.monotonic()

    def log(text):
        print("[%7.2f] %s" % (time.monotonic() - started, text), flush=True)

    try:
        first_address = ipaddress.IPv4Address(options.first_address)
        last_address = ipaddress.IPv4Address(int(first_address) + max(options.machines, 1) - 1)
    except ValueError as error:
        parser.error("--first-address: %s" % error)
    if first_address.is_loopback and not last_address.is_loopback:
        parser.error("--first-address: %d machines from %s run past 127.255.255.255" % (options.machines, first_address))
    if not first_address.is_loopback:
        log("warning: %s is not a loopback address; the machines bind real addresses" % first_address)
    machines = []
    for index in range(options.machines):
        address = str(first_address + index)
        machine = Machine(index + 1, address, options.host, log)
        machine.state = "waiting"
        machine.load_seconds = options.load_seconds
        machine.wander = options.wander
        if options.team in ("host", "split"):
            machine.team_host = True
            machine.team_split = options.team == "split"
        elif options.team is not None:
            machine.wanted_team = int(options.team)
        machines.append(machine)

    gather = None
    if options.gather and options.positions:
        gather = {"target": None, "positions": {}, "radius": options.gather_radius}
        if not options.gather.startswith("machine:"):
            gather["target"] = tuple(float(v) for v in options.gather.split(","))[:2]
        for machine in machines:
            machine.gather = gather
    last_positions_read = 0
    first_ingame_time = None
    board = None
    if options.board and options.positions and options.vehicles:
        board = {"positions": {}, "vehicles": {}, "seats": {}, "seated": set(), "claims": {},
                 "taken": set(), "vehicle_teams": {}, "teams": options.team is not None,
                 "drivers": options.board_drivers,
                 "words": [word.strip().lower() for word in options.board.split(",") if word.strip()]}
        for machine in machines:
            machine.board = board
    last_board_read = 0

    # machines connect a few at a time: a host accepts connections from its
    # frame loop, and one whose listen backlog is full refuses the rest
    selector = selectors.DefaultSelector()
    waiting = list(machines)
    next_connect_time = 0
    log("connecting %d machines to %s:%d" % (len(machines), options.host, SERVER_PORT))

    start_requested = False
    all_in_time = None
    last_status = 0
    last_input = 0
    try:
        while True:
            now = time.monotonic()
            if waiting and now >= next_connect_time:
                machine = next((m for m in waiting if m.retry_time <= now), None)
                if machine:
                    waiting.remove(machine)
                    machine.connect()
                    selector.register(machine.tcp, selectors.EVENT_READ | selectors.EVENT_WRITE, machine)
                    next_connect_time = now + 1.0 / options.join_rate
            # Windows' select() refuses an empty set: while every machine waits
            # to try again (no game hosted yet), just wait
            if selector.get_map():
                ready = selector.select(timeout=0.005)
            else:
                time.sleep(0.005)
                ready = []
            for key, events in ready:
                machine = key.data
                if machine.state == "connecting" and events & selectors.EVENT_WRITE:
                    error = machine.tcp.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                    if error:
                        machine.close(selector)
                        if error in (errno.ECONNREFUSED, 10061) and machine.connect_attempts < 20:
                            machine.state = "waiting"
                            machine.retry_time = now + 0.5
                            waiting.append(machine)
                        else:
                            log("%s: connect failed (%d)" % (machine.name, error))
                            machine.state = "closed"
                        continue
                    selector.modify(machine.tcp, selectors.EVENT_READ, machine)
                    machine.joined()
                if events & selectors.EVENT_READ and machine.state != "closed":
                    try:
                        if not machine.receive() or machine.state == "closed":
                            machine.close(selector)
                    except OSError as error:
                        # a reply the host stopped reading, or a reset
                        log("%s: %s" % (machine.name, error))
                        machine.close(selector)
            if gather is not None and now - last_positions_read >= 0.1:
                last_positions_read = now
                try:
                    with open(options.positions) as dump:
                        lines = dump.read().split("\n")
                    if "end" in lines:
                        positions = {}
                        for line in lines:
                            fields = line.split()
                            if len(fields) == 4:
                                positions[int(fields[0])] = tuple(float(v) for v in fields[1:])
                        gather["positions"] = positions
                except (OSError, ValueError):
                    pass
                if first_ingame_time is None and any(m.state == "ingame" for m in machines):
                    first_ingame_time = now
                if (gather["target"] is None and first_ingame_time is not None and
                        now - first_ingame_time >= 3.0):
                    who = int(options.gather.split(":")[1])
                    if who in gather["positions"]:
                        gather["target"] = gather["positions"][who][:2]
                        log("gathering at %.1f, %.1f (where machine %d's player stands)" % (
                            gather["target"][0], gather["target"][1], who))
            if board is not None and now - last_board_read >= 0.1:
                last_board_read = now
                try:
                    with open(options.positions) as dump:
                        lines = dump.read().split("\n")
                    if "end" in lines:
                        positions = {}
                        for line in lines:
                            fields = line.split()
                            if len(fields) == 4:
                                positions[int(fields[0])] = tuple(float(v) for v in fields[1:])
                        board["positions"] = positions
                    with open(options.vehicles) as dump:
                        lines = dump.read().split("\n")
                    if "end" in lines:
                        vehicles, seats, seated = {}, {}, set()
                        for line in lines:
                            fields = line.split()
                            if not fields:
                                continue
                            if fields[0] == "seated":
                                seated.add(int(fields[1]))
                            elif fields[0] == "vehicle" and len(fields) >= 6:
                                if any(word in fields[5].lower() for word in board["words"]):
                                    vehicles[int(fields[1])] = tuple(float(v) for v in fields[2:5])
                            elif fields[0] == "seat" and len(fields) >= 9 and int(fields[1]) in vehicles:
                                seats[(int(fields[1]), int(fields[2]))] = {
                                    "entrance": tuple(float(v) for v in fields[3:6]),
                                    "free": fields[6] == "1", "driver": fields[7] == "1",
                                    "waits": fields[8] == "1",
                                    "seat": tuple(float(v) for v in fields[9:12]) if len(fields) >= 12
                                    else tuple(float(v) for v in fields[3:6])}
                        board["vehicles"], board["seats"], board["seated"] = vehicles, seats, seated
                        # who sits where: a seated player is on its seat, in the
                        # nearest vehicle; its team is the lobby's
                        team_of = {m.machine_index: m.team_index for m in machines if m.machine_index is not None}
                        host_team = next((m.wanted_team for m in machines if m.team_host and m.wanted_team is not None
                                          and m.index % 2 == 0), None)
                        team_of.setdefault(0, host_team)
                        taken, vehicle_teams = set(), {}
                        for machine_index in seated:
                            position = board["positions"].get(machine_index)
                            if position is None:
                                continue
                            nearest = min(seats.items(), key=lambda item: math.dist(item[1]["seat"], position),
                                          default=None)
                            if nearest is None or math.dist(nearest[1]["seat"], position) > 3.0:
                                continue
                            taken.add(nearest[0])
                            vehicle_teams.setdefault(nearest[0][0], set()).add(team_of.get(machine_index))
                        board["taken"], board["vehicle_teams"] = taken, vehicle_teams
                except (OSError, ValueError):
                    pass
            if now - last_input >= 1.0 / options.rate:
                last_input = now
                for machine in machines:
                    if machine.state != "closed":
                        try:
                            machine.tick(now)
                        except OSError as error:
                            log("%s: %s" % (machine.name, error))
                            machine.close(selector)
            if options.start and not start_requested:
                ready = [m for m in machines if m.state == "pregame" and m.player_added and m.settings_complete and
                         m.team_ready() and (not m.team_host or m.wanted_team is not None)]
                if len(ready) == len(machines) and all_in_time is None:
                    all_in_time = now
                    log("all %d machines are in the lobby" % len(machines))
                if all_in_time is not None and now - all_in_time >= options.start_delay:
                    start_requested = True
                    log("asking the host to start the game")
                    try:
                        machines[0].send(message(CLIENT_GAME_START_REQUEST,
                                                 struct.pack(">h", COUNTDOWN_EVENT_START_IMMEDIATELY)))
                    except OSError as error:
                        log("%s: %s" % (machines[0].name, error))
                        machines[0].close(selector)
            if now - last_status >= options.status_every:
                last_status = now
                states = {}
                for machine in machines:
                    states[machine.state] = states.get(machine.state, 0) + 1
                sample = next((m for m in machines if m.settings_complete), None)
                players = machines_in_game = None
                if sample:
                    for machine_slots in (128, 4):
                        layout = network_game_layout(machine_slots, 128 if machine_slots == 128 else 16)
                        if len(sample.settings_complete) == layout["size"]:
                            machines_in_game = struct.unpack_from("<h", sample.settings_complete, layout["machine_count"])[0]
                            players = struct.unpack_from("<h", sample.settings_complete, layout["player_count"])[0]
                updates = [m.last_update_number for m in machines if m.last_update_number is not None]
                log("states %s; host game: %s machines, %s players; latest update %s; received %.1f MB" % (
                    states, machines_in_game, players, max(updates) if updates else None,
                    sum(m.bytes_received for m in machines) / 1e6))
                if gather is not None and gather["target"] is not None:
                    distances = sorted(
                        math.hypot(p[0] - gather["target"][0], p[1] - gather["target"][1])
                        for i, p in gather["positions"].items() if i != 0)
                    log("gathering: %d stopped; median distance %.1f, furthest %.1f" % (
                        sum(1 for m in machines if m.stopped),
                        distances[len(distances) // 2] if distances else -1,
                        distances[-1] if distances else -1))
                if board is not None:
                    log("boarding: %d seated of %d; %d vehicles, %d free seats; %d making for a seat" % (
                        sum(1 for m in machines if m.machine_index in board["seated"]), len(machines),
                        len(board["vehicles"]),
                        sum(1 for key, seat in board["seats"].items()
                            if key not in board["taken"] and not seat["waits"] and
                            (board["drivers"] or not seat["driver"])),
                        sum(1 for m in machines if m.board_seat is not None)))
            if options.seconds and now - started >= options.seconds:
                break
            if all(m.state in ("closed", "rejected") for m in machines):
                log("every machine has left")
                break
    except KeyboardInterrupt:
        pass
    for machine in machines:
        if machine.tcp:
            machine.tcp.close()
        machine.udp.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
