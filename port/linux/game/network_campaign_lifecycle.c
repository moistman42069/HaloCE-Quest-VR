/* Campaign loading/BSP barriers. Transport continues while simulation is held.
 * No remote memory image, pointer or arbitrary script is accepted. */
#include "cseries.h"
#include "game/game.h"
#include "game/player_queues_new.h"
#include "networking/network_game_globals.h"
#include "networking/network_game_manager.h"
#include "scenario/scenario.h"
#include "scenario/scenario_definitions.h"
#include "network_distributed.h"
#include "network_campaign.h"
#include <string.h>

void platform_log(char const *format, ...);
unsigned long system_milliseconds(void);
void game_time_set_distributed(long time);
void render_interpolation_reset(void);

enum { CAMPAIGN_READY = 1, CAMPAIGN_BSP, CAMPAIGN_ACK, CAMPAIGN_RELEASE, CAMPAIGN_FAILED,
	CAMPAIGN_SAVE, CAMPAIGN_RESTORE };
enum { PHASE_IDLE, PHASE_HOST_WAIT, PHASE_CLIENT_WAIT, PHASE_CLIENT_APPLY, PHASE_CLIENT_SNAPSHOT };
struct campaign_barrier
{
	long round;
	unsigned long seed, serial;
	long time;
	short operation, bsp;
	unsigned long epoch;
	byte digest[32];
};
typedef char campaign_barrier_size_assert[sizeof(struct campaign_barrier) == 56 ? 1 : -1];
static struct campaign_barrier barrier;
static byte local_digest[32];
static short phase;
static unsigned long epoch, started, last_send, serial;
static boolean applying, content_valid, peer_ack, local_applied, checkpoint_valid;
static long peer_machine = NONE;
static short deferred_checkpoint;

static void campaign_fail(char const *reason)
{
	platform_log("campaign: %s; ending session", reason);
	phase = PHASE_IDLE;
	content_valid = FALSE;
	network_game_abort();
}

word network_campaign_lifecycle_size(void) { return sizeof(struct campaign_barrier); }
boolean network_campaign_held(void) { return network_campaign_active() && phase != PHASE_IDLE; }
boolean network_campaign_accept_state(void)
{
	return !network_campaign_active() || (content_valid &&
		(phase == PHASE_IDLE || phase == PHASE_CLIENT_SNAPSHOT));
}

/* Campaign-only interpretation of the existing tick field: 8-bit generation,
 * 24-bit tick (over six days at 30 Hz). Never wrap a generation within a map. */
long network_campaign_encode_time(long time)
{
	return network_campaign_active() ? (long)((epoch << 24) | ((unsigned long)time & 0xFFFFFFUL)) : time;
}
boolean network_campaign_decode_time(long *time)
{
	if (!network_campaign_active()) return TRUE;
	if (((unsigned long)*time >> 24) != epoch || !content_valid) return FALSE;
	*time = (long)((unsigned long)*time & 0xFFFFFFUL);
	return TRUE;
}

static void send_barrier(short operation)
{
	struct { struct distributed_message_header header; struct campaign_barrier entry; } message;
	message.entry = barrier;
	message.entry.operation = operation;
	memcpy(message.entry.digest, local_digest, sizeof(local_digest));
	distributed_send(&message, _distributed_message_campaign_lifecycle, 1, sizeof(message),
		game_connection() == _game_connection_network_server ? _distributed_to_clients_reliably : _distributed_to_host_reliably);
	last_send = system_milliseconds();
}

static void host_begin(short operation, short bsp)
{
	if (epoch >= 255 || game_time_get() < 0 || game_time_get() > 0xFFFFFFL)
	{ campaign_fail("campaign generation or tick limit reached; start a new session"); return; }
	memset(&barrier, 0, sizeof(barrier));
	barrier.round = network_game_get_number_of_games_played();
	barrier.seed = network_game_get_random_seed();
	barrier.serial = ++serial;
	barrier.time = game_time_get();
	barrier.operation = operation;
	barrier.bsp = bsp;
	barrier.epoch = ++epoch;
	phase = PHASE_HOST_WAIT;
	peer_ack = FALSE;
	local_applied = operation == CAMPAIGN_READY || operation == CAMPAIGN_BSP;
	started = system_milliseconds();
	last_send = 0;
	platform_log("campaign: barrier %lu operation %d BSP %d tick %ld", serial, operation, bsp, barrier.time);
}

void network_campaign_loaded(void)
{
	phase = PHASE_IDLE;
	applying = peer_ack = content_valid = FALSE;
	peer_machine = NONE;
	serial = 0;
	checkpoint_valid = FALSE;
	deferred_checkpoint = 0;
	if (!network_campaign_active()) return;
	content_valid = cache_files_campaign_digest(network_game_get_game()->map.name, local_digest);
	if (!content_valid) { campaign_fail("could not hash campaign map/resources"); return; }
	/* Keep generations unique across missions too: a delayed generic object
	 * datagram has no round/seed of its own. New process connections start at 0. */
	started = system_milliseconds();
	last_send = 0;
	if (game_connection() == _game_connection_network_server)
		host_begin(CAMPAIGN_READY, global_structure_bsp_index);
	else phase = PHASE_CLIENT_WAIT;
}

boolean network_campaign_checkpoint_request(boolean restore)
{
	if (!network_campaign_active() || applying) return FALSE;
	/* A client cannot independently roll the world back or save a checkpoint. */
	if (game_connection() != _game_connection_network_server) return TRUE;
	if (phase != PHASE_IDLE)
	{
		deferred_checkpoint = restore ? 2 : MAX(deferred_checkpoint, 1);
		platform_log("campaign: checkpoint request deferred during a transition");
		return TRUE;
	}
	if (restore && (!checkpoint_valid || !game_state_campaign_has_checkpoint()))
	{
		platform_log("campaign: no shared checkpoint yet; restarting mission together");
		network_campaign_change_level(FALSE);
		return TRUE;
	}
	host_begin(restore ? CAMPAIGN_RESTORE : CAMPAIGN_SAVE, global_structure_bsp_index);
	return TRUE;
}

void network_campaign_bsp_switched(short bsp)
{
	if (!applying && network_campaign_playing() && game_connection() == _game_connection_network_server)
	{
		if (phase != PHASE_IDLE) { campaign_fail("overlapping campaign BSP transitions"); return; }
		host_begin(CAMPAIGN_BSP, bsp);
	}
}

void network_campaign_level_wait(void)
{
	phase = PHASE_CLIENT_WAIT;
	content_valid = FALSE;
	deferred_checkpoint = 0;
}

void network_campaign_lifecycle_receive(long machine, void const *entry, word size)
{
	struct campaign_barrier incoming;
	if (!network_campaign_playing() || size != sizeof(incoming)) return;
	memcpy(&incoming, entry, sizeof(incoming));
	if (incoming.round != network_game_get_number_of_games_played() ||
		incoming.seed != (unsigned long)network_game_get_random_seed() ||
		!incoming.serial || incoming.epoch < 1 || incoming.epoch > 255 ||
		incoming.time < 0 || incoming.time > 0xFFFFFFL ||
		!VALID_INDEX(incoming.bsp, global_scenario_get()->structure_bsp_references.count)) return;
	if (game_connection() == _game_connection_network_server)
	{
		long machines[2];
		if (machine == NONE || distributed_client_machines(machines, 2) != 1 || machines[0] != machine ||
			phase != PHASE_HOST_WAIT || incoming.serial != barrier.serial || incoming.epoch != epoch) return;
		if (incoming.operation == CAMPAIGN_FAILED || memcmp(local_digest, incoming.digest, sizeof(local_digest)))
		{ campaign_fail("peer has different map/resources or failed transition"); return; }
		if (incoming.operation == CAMPAIGN_ACK && incoming.bsp == barrier.bsp)
		{ peer_ack = TRUE; peer_machine = machine; }
		return;
	}
	if (machine != NONE || game_connection() != _game_connection_network_client) return;
	if (memcmp(local_digest, incoming.digest, sizeof(local_digest)))
	{ campaign_fail("host has different campaign map/resources"); return; }
	if (incoming.operation == CAMPAIGN_RELEASE)
	{
		if (phase != PHASE_CLIENT_SNAPSHOT || incoming.serial != barrier.serial || incoming.epoch != epoch) return;
		if (!network_objects_synchronized()) { campaign_fail("object snapshot incomplete at release"); return; }
		game_time_set_distributed(incoming.time);
		network_game_client_campaign_clock(incoming.time);
		update_queues_reset_and_fill_with_lies();
		if (barrier.operation == CAMPAIGN_SAVE) checkpoint_valid = TRUE;
		phase = PHASE_IDLE;
		platform_log("campaign: resumed barrier %lu at tick %ld", incoming.serial, incoming.time);
		return;
	}
	if (incoming.operation != CAMPAIGN_READY && incoming.operation != CAMPAIGN_BSP &&
		incoming.operation != CAMPAIGN_SAVE && incoming.operation != CAMPAIGN_RESTORE) return;
	if (incoming.serial < serial) return;
	if (incoming.serial == serial)
	{
		if (phase == PHASE_CLIENT_SNAPSHOT) send_barrier(CAMPAIGN_ACK);
		return;
	}
	if (phase != PHASE_IDLE && phase != PHASE_CLIENT_WAIT) return;
	if (incoming.operation == CAMPAIGN_READY && phase != PHASE_CLIENT_WAIT) return;
	barrier = incoming;
	serial = incoming.serial;
	epoch = incoming.epoch;
	phase = PHASE_CLIENT_APPLY;
	started = system_milliseconds();
}

void network_campaign_frame(void)
{
	unsigned long now = system_milliseconds();
	if (!network_campaign_active()) { phase = PHASE_IDLE; content_valid = FALSE; return; }
	if (!network_campaign_playing()) return;
	if (phase == PHASE_IDLE)
	{
		if (deferred_checkpoint)
		{
			short request = deferred_checkpoint;
			deferred_checkpoint = 0;
			network_campaign_checkpoint_request(request == 2);
		}
		return;
	}
	if (now - started > 120000UL) { campaign_fail("campaign transition timed out"); return; }
	if (phase == PHASE_CLIENT_APPLY)
	{
		boolean success = TRUE;
		applying = TRUE;
		if (barrier.operation == CAMPAIGN_RESTORE)
			success = checkpoint_valid && game_state_campaign_restore();
		else if (global_structure_bsp_index != barrier.bsp) success = scenario_switch_structure_bsp(barrier.bsp);
		if (success && barrier.operation == CAMPAIGN_SAVE) success = game_state_campaign_save();
		applying = FALSE;
		if (!success || global_structure_bsp_index != barrier.bsp)
		{ send_barrier(CAMPAIGN_FAILED); campaign_fail("campaign transition could not be applied"); return; }
		if (barrier.operation == CAMPAIGN_RESTORE) network_campaign_script_reset();
		network_distributed_resynchronize();
		game_time_set_distributed(barrier.time);
		update_queues_reset_and_fill_with_lies();
		phase = PHASE_CLIENT_SNAPSHOT;
		render_interpolation_reset();
		send_barrier(CAMPAIGN_ACK);
	}
	else if (phase == PHASE_HOST_WAIT)
	{
		if (!local_applied)
		{
			boolean success;
			applying = TRUE;
			success = barrier.operation == CAMPAIGN_SAVE ? game_state_campaign_save() : game_state_campaign_restore();
			applying = FALSE;
			if (!success) { campaign_fail("host checkpoint I/O failed"); return; }
			local_applied = TRUE;
			barrier.time = game_time_get();
			barrier.bsp = global_structure_bsp_index;
			if (barrier.operation == CAMPAIGN_RESTORE) network_campaign_script_reset();
		}
		if (peer_ack)
		{
			network_distributed_resynchronize();
			render_interpolation_reset();
			network_game_server_campaign_clock(game_time_get());
			network_game_client_campaign_clock(game_time_get());
			update_queues_reset_and_fill_with_lies();
			network_distributed_campaign_snapshot(peer_machine);
			barrier.time = game_time_get();
			send_barrier(CAMPAIGN_RELEASE);
			if (barrier.operation == CAMPAIGN_SAVE) checkpoint_valid = TRUE;
			phase = PHASE_IDLE;
			platform_log("campaign: released barrier %lu", barrier.serial);
		}
		else if (!last_send || now - last_send >= 2000UL) send_barrier(barrier.operation);
	}
}
