/* Online campaign is a separate protocol, never an extension accepted by a
 * stock competitive client. No network_game wire layout changes are needed. */
#ifndef NETWORK_CAMPAIGN_H
#define NETWORK_CAMPAIGN_H

#define HALO_CAMPAIGN_NETWORK_VERSION 0xCE01
/* CE01 only: upstream PvP uses this bit for an in-progress match. */
#define HALO_CAMPAIGN_ADVERTISED_FLAG 0x02
#define HALO_CAMPAIGN_MAP_VERSION 0x434F0001L

struct network_game;
boolean network_campaign_game(struct network_game const *game);
boolean network_campaign_active(void);
boolean network_campaign_client(void);
boolean network_campaign_playing(void);
boolean network_campaign_advertised(word version, byte flags);
void network_campaign_join_token(byte *token);
boolean network_campaign_prepare(struct network_game *game, char const *map, short difficulty);
void network_campaign_session_update(boolean menu_loaded, real seconds);
boolean network_campaign_host_settings(struct network_game *game);
boolean network_campaign_host_requested(void);
boolean network_campaign_change_level(boolean next);
void network_campaign_session_end(void);
void network_campaign_level_wait(void);
void network_campaign_loaded(void);
void network_campaign_frame(void);
boolean network_campaign_held(void);
void network_campaign_bsp_switched(short bsp);
void network_campaign_lifecycle_receive(long machine, void const *entry, word size);
word network_campaign_lifecycle_size(void);
long network_campaign_encode_time(long time);
boolean network_campaign_decode_time(long *time);
boolean network_campaign_accept_state(void);
void network_distributed_resynchronize(void);
void network_distributed_campaign_snapshot(long machine);
boolean network_objects_synchronized(void);
boolean cache_files_campaign_digest(char const *map_name, byte *digest);
boolean network_campaign_checkpoint_request(boolean restore);
boolean game_state_campaign_save(void);
boolean game_state_campaign_restore(void);
boolean game_state_campaign_has_checkpoint(void);
void network_game_client_campaign_clock(long time);
void network_game_server_campaign_clock(long time);
void network_campaign_script_capture(short function_index, long const *arguments);
void network_campaign_script_capture_named(char const *name, long const *arguments);
void network_campaign_script_flush(void);
void network_campaign_script_reset(void);
word network_campaign_script_entry_size(void);
void network_campaign_script_receive(void const *entries, short count);

/* Replay is restricted to the presentation allowlist. No script source,
 * pointers, console commands or simulation functions travel on the wire. */
boolean hs_campaign_call_valid(short function_index, long const *arguments);
void hs_campaign_replay(short function_index, long *arguments);

struct campaign_device_state
{
	long round;
	unsigned long seed;
	long object_index;
	real power, power_velocity, position, position_velocity, power_target, position_target;
	unsigned long flags, machine_flags;
	short delay_ticks;
	word power_flags, position_flags, reserved;
};
boolean device_campaign_read(long object_index, struct campaign_device_state *state);
void device_campaign_apply(struct campaign_device_state const *state);
void network_campaign_devices_tick(void);
void network_campaign_devices_reset(void);
void network_campaign_devices_receive(void const *entries, short count);
void network_campaign_objects_tick(void);
void network_campaign_objects_reset(void);
word network_campaign_objects_size(void);
void network_campaign_objects_receive(void const *entries, short count);
struct unit_control_data;
void network_campaign_actor_capture(long object_index, struct unit_control_data const *control);
void network_campaign_actor_update(long object_index);
union real_vector2d;
void network_campaign_actor_impulse_capture(long object_index, short impulse, union real_vector2d const *alignment);
word network_campaign_actor_impulses_size(void);
void network_campaign_actor_impulses_reset(void);
void network_campaign_actor_impulses_receive(void const *entries, short count);
void network_campaign_actors_tick(void);
void network_campaign_actors_reset(void);
word network_campaign_actors_size(void);
void network_campaign_actors_receive(void const *entries, short count);

#endif
