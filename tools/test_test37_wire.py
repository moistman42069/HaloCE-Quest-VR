"""Exercise the production Halo network packet codec and settings-fragment reassembly.

The C fixture links the real network_messages/data_packet/message-header sources.
It does not reimplement packet encoding. The reassembly routine and message
structure are extracted verbatim from network_client_message_handler.c.
Requires Linux/WSL clang; no game, device, server, or copyrighted data is used.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/test37-wire"
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def function(source, name):
    match = re.search(
        r"^(?:static )?(?:inline )?[\w *]+\b" + re.escape(name) + r"\s*\([^;{]*\)\s*\{",
        source,
        re.M,
    )
    assert match, f"missing production function: {name}"
    start = source.index("{", match.start())
    depth, end = 1, start + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


messages = read("source/networking/network_messages.c")
client_handler = read("source/networking/network_client_message_handler.c")
server_handler = read("source/networking/network_server_message_handler.c")
limits = read("port/linux/include/halo_port_limits.h")

# Confirm the test's fixture dimensions/schema against the production table.
assert "DEFINE_NETWORK_GAME_MESSAGE(message_server_game_advertise, 0x114);" in messages
assert "DEFINE_NETWORK_GAME_MESSAGE(message_server_game_settings_update, 8 + HALO_PORT_NETWORK_GAME_SETTINGS_FRAGMENT_SIZE);" in messages
assert "#define HALO_PORT_NETWORK_GAME_SETTINGS_FRAGMENT_SIZE 0xE00" in limits
assert re.search(r"^#define HALO_PORT_NETWORK_VERSION 24$", limits, re.M)
assert re.search(
    r"server_game_advertise_fields\[2\];.*?DATA_PACKET_FIELD\(_data_packet_field_raw, 276\)",
    messages,
    re.S,
)
assert re.search(
    r"server_game_settings_update_fields\[4\];.*?"
    r"DATA_PACKET_FIELD\(_data_packet_field_shorts, 3\),\s*"
    r"DATA_PACKET_FIELD\(_data_packet_field_pad, 2\),\s*"
    r"DATA_PACKET_FIELD\(_data_packet_field_raw, HALO_PORT_NETWORK_GAME_SETTINGS_FRAGMENT_SIZE\)",
    messages,
    re.S,
)

# Discovery advertises the immutable local host protocol (24), not the
# client-side selectable join target. Its full native structure is passed to
# the production raw packet codec below.
advertise = function(
    server_handler, "network_game_server_handle_message_client_broadcast_game_search"
)
assert "advertisement.reserved[HALO_PORT_ADVERTISED_VERSION_OFFSET] = (byte)(HALO_PORT_NETWORK_VERSION & 0xFF);" in advertise
assert "advertisement.reserved[HALO_PORT_ADVERTISED_VERSION_OFFSET + 1] = (byte)(HALO_PORT_NETWORK_VERSION >> 8);" in advertise
assert "HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG" in advertise
assert "halo_port_active_network_version()" not in advertise

settings_struct = re.search(
    r"struct message_server_game_settings_update\s*\{[^}]*\};", client_handler, re.S
)
assert settings_struct, "missing production settings-fragment struct"
reassembly = function(client_handler, "network_game_client_receive_game_settings_piece")

fixture = r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cseries/cseries.h"
#include "networking/network_messages.h"
#include "bungie_net/common/message_header.h"

#define CHECK(expression) do { if (!(expression)) { \
    fprintf(stderr, "wire fixture check failed at %s:%d: %s\n", __FILE__, __LINE__, #expression); \
    abort(); \
} } while (0)

struct network_game { byte bytes[HALO_PORT_NETWORK_GAME_SIZE]; };
struct network_game_client {
    int settings_callbacks;
    byte applied_settings[HALO_PORT_NETWORK_GAME_SIZE];
};

''' + settings_struct.group(0) + r'''

static struct network_game network_game_client_settings_staging;
static long network_game_client_settings_staging_size = 0;
static long emitted_network_events = 0;

static boolean network_game_client_game_settings_updated(
    struct network_game_client *client,
    struct network_game *game)
{
    CHECK(client != NULL && game != NULL);
    client->settings_callbacks++;
    csmemcpy(client->applied_settings, game->bytes, sizeof(game->bytes));
    return TRUE;
}

''' + reassembly + r'''

static void roundtrip_packet(
    short type,
    short packet_class,
    const void *source,
    short source_size,
    void *destination,
    short expected_wire_size)
{
    void *outer = create_network_game_message(
        (enum network_game_message_type)type, source, source_size);
    CHECK(outer != NULL);

    word header = *(word *)outer;
    CHECK(GET_MESSAGE_TYPE(header) == _message_type_packet);
    if (GET_MESSAGE_SIZE(header) != (word)expected_wire_size)
        fprintf(stderr, "wire-size mismatch: type=%d actual=%u expected=%d header=%04x\\n",
            type, (unsigned)GET_MESSAGE_SIZE(header), expected_wire_size, header);
    CHECK(GET_MESSAGE_SIZE(header) == (word)expected_wire_size);

    short encoded_size = (short)(GET_MESSAGE_SIZE(header) - sizeof(word));
    short decoded_type = 0;
    short decoded_version = 1;
    CHECK(decode_network_game_message(
        destination,
        (byte *)outer + sizeof(word),
        &encoded_size,
        &decoded_type,
        &decoded_version,
        packet_class));
    CHECK(decoded_type == type);
    CHECK(decoded_version == 1);
}

static void test_advertisement_codec(void)
{
    byte source[0x114];
    byte decoded[sizeof(source)];
    for (size_t i = 0; i < sizeof(source); i++)
        source[i] = (byte)((i * 73u + 19u) & 0xFFu);
    csmemset(decoded, 0, sizeof(decoded));

    /* message_server_game_advertise uses its production 276-byte raw field;
       type 2 belongs to the server advertisement packet class (1). */
    roundtrip_packet(_message_server_game_advertise, 1,
        source, sizeof(source), decoded, sizeof(source) + 4);
    CHECK(csmemcmp(source, decoded, sizeof(source)) == 0);
}

static void make_piece(
    struct message_server_game_settings_update *piece,
    const byte *settings,
    word offset,
    word length)
{
    csmemset(piece, 0, sizeof(*piece));
    piece->total_size = HALO_PORT_NETWORK_GAME_SIZE;
    piece->offset = offset;
    piece->length = length;
    csmemcpy(piece->data, settings + offset, length);
}

static void test_fragment_wire_and_reassembly(void)
{
    byte settings[HALO_PORT_NETWORK_GAME_SIZE];
    byte fragment[HALO_PORT_NETWORK_GAME_SETTINGS_FRAGMENT_SIZE];
    struct message_server_game_settings_update source_piece;
    struct message_server_game_settings_update decoded_piece;
    struct network_game_client client = {0};

    for (size_t i = 0; i < sizeof(settings); i++)
        settings[i] = (byte)((i * 29u + (i >> 5) + 7u) & 0xFFu);

    /* The 0xE00 production chunk size requires four fragments for the
       production 0x3340-byte game settings record. Each fragment traverses
       create_network_game_message and decode_network_game_message. */
    CHECK(sizeof(settings) == 0x3340);
    CHECK((sizeof(settings) + sizeof(source_piece.data) - 1) / sizeof(source_piece.data) == 4);
    for (word offset = 0; offset < sizeof(settings); offset += sizeof(source_piece.data)) {
        word length = (word)((sizeof(settings) - offset) < sizeof(source_piece.data)
            ? sizeof(settings) - offset : sizeof(source_piece.data));
        make_piece(&source_piece, settings, offset, length);
        csmemset(&decoded_piece, 0xCC, sizeof(decoded_piece));
        roundtrip_packet(_message_server_game_settings_update, 2,
            &source_piece, sizeof(source_piece),
            &decoded_piece, sizeof(source_piece) + 2); /* 2-byte pad omitted; version + type + outer header added */
        CHECK(decoded_piece.total_size == source_piece.total_size);
        CHECK(decoded_piece.offset == source_piece.offset);
        CHECK(decoded_piece.length == source_piece.length);
        CHECK(decoded_piece.pad == 0xCCCC); /* pad is intentionally absent on wire and ignored on decode */
        CHECK(csmemcmp(decoded_piece.data, source_piece.data, sizeof(fragment)) == 0);
        CHECK(network_game_client_receive_game_settings_piece(&client, &decoded_piece));
    }
    CHECK(client.settings_callbacks == 1);
    CHECK(csmemcmp(client.applied_settings, settings, sizeof(settings)) == 0);
    CHECK(network_game_client_settings_staging_size == 0);

    /* A mismatched game-layout size is rejected and clears the partial copy. */
    make_piece(&source_piece, settings, 0, sizeof(source_piece.data));
    source_piece.total_size--;
    CHECK(!network_game_client_receive_game_settings_piece(&client, &source_piece));
    CHECK(network_game_client_settings_staging_size == 0);
    CHECK(client.settings_callbacks == 1);

    /* A valid first piece followed by a skipped offset resets staging; the
       later record cannot be applied until a new offset-zero piece arrives. */
    make_piece(&source_piece, settings, 0, sizeof(source_piece.data));
    CHECK(network_game_client_receive_game_settings_piece(&client, &source_piece));
    make_piece(&source_piece, settings, sizeof(source_piece.data) * 2,
        sizeof(source_piece.data));
    CHECK(network_game_client_receive_game_settings_piece(&client, &source_piece));
    CHECK(network_game_client_settings_staging_size == 0);
    CHECK(client.settings_callbacks == 1);

    /* An oversized fragment is rejected before copying. */
    make_piece(&source_piece, settings, 0, sizeof(source_piece.data));
    source_piece.length = sizeof(source_piece.data) + 1;
    CHECK(!network_game_client_receive_game_settings_piece(&client, &source_piece));
    CHECK(network_game_client_settings_staging_size == 0);
    CHECK(client.settings_callbacks == 1);
}

int main(void)
{
    word endian_probe = 1;
    CHECK(*(byte *)&endian_probe == 1); /* native OpenCE packets use little-endian host fields */
    test_advertisement_codec();
    test_fragment_wire_and_reassembly();
    CHECK(emitted_network_events >= 3);
    puts("PASS: production advertisement/settings packet codec, 4-fragment record roundtrip, ordering/layout guards");
    return 0;
}

/* Minimal host services used only by exercised production code. */
char temporary[256];
unsigned long system_milliseconds(void) { return 1; }
void error(short priority, const char *format, ...) {
    (void)priority; (void)format; emitted_network_events++;
}
void display_assert(char *information, char *file, long line, boolean fatal) {
    fprintf(stderr, "unexpected production assertion: %s (%s:%ld, fatal=%d)\n",
        information ? information : "<none>", file ? file : "<none>", line, fatal);
    abort();
}
void system_exit(long code) { fprintf(stderr, "unexpected system_exit(%ld)\n", code); abort(); }
void *csmemset(void *buffer, long value, unsigned long size) {
    return __builtin_memset(buffer, (int)value, size);
}
void *csmemcpy(void *destination, const void *source, unsigned long size) {
    return __builtin_memcpy(destination, source, size);
}
long csmemcmp(const void *left, const void *right, unsigned long size) {
    return __builtin_memcmp(left, right, size);
}
char *csstrcpy(char *destination, const char *source) {
    char *result = destination;
    while ((*destination++ = *source++) != 0) { }
    return result;
}
char *csstrncpy(char *destination, const char *source, unsigned long size) {
    char *result = destination;
    while (size && (*destination++ = *source++) != 0) size--;
    while (size--) *destination++ = 0;
    return result;
}
char *csprintf(char *buffer, char *format, ...) {
    va_list args; va_start(args, format); vsprintf(buffer, format, args); va_end(args); return buffer;
}
void *debug_malloc(unsigned int size, boolean clear, const char *file, long line) {
    (void)clear; (void)file; (void)line; return __builtin_malloc(size);
}
'''

cfile = OUT / "production_wire_fixture.c"
binary = OUT / "production_wire_fixture"
semantics = OUT / "host_msvc_semantics.h"
cfile.write_text(fixture, encoding="utf-8")
semantics.write_text("#pragma weak fast_ftol\n", encoding="utf-8")
subprocess.run(
    [
        "clang",
        "-std=gnu89",
        "-fms-extensions",
        "-D__STRICT_ANSI__",
        "-DHALO_LINUX_PLATFORM_LAYER",
        "-O1",
        "-g",
        "-w",
        "-fsanitize=address",
        "-Wno-unused-function",
        "-Wno-unused-variable",
        "-Wno-microsoft-anon-tag",
        "-fshort-wchar",
        "-ffunction-sections",
        "-fdata-sections",
        "-I",
        str(ROOT / "source"),
        "-I",
        str(ROOT / "source/cseries"),
        "-I",
        str(ROOT / "port/linux/include"),
        "-include",
        str(ROOT / "port/linux/include/halo_port_limits.h"),
        "-include",
        str(semantics),
        str(cfile),
        str(ROOT / "source/networking/network_messages.c"),
        str(ROOT / "source/memory/data_packet_groups.c"),
        str(ROOT / "source/memory/data_packets.c"),
        str(ROOT / "source/memory/data_encoding.c"),
        str(ROOT / "source/memory/byte_swapping.c"),
        str(ROOT / "source/bungie_net/common/message_header.c"),
        "-Wl,--gc-sections",
        "-o",
        str(binary),
    ],
    check=True,
)
subprocess.run([str(binary)], check=True)
print("PASS: production OpenCE packet wire fixture and settings reassembly guards")
