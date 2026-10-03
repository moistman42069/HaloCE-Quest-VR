/* Campaign object presentation not carried by the competitive transform stream.
 * Inventories and occupied vehicle seats keep their existing dedicated paths. */
#include "cseries.h"
#include "game/game.h"
#include "objects/objects.h"
#include "objects/object_definitions.h"
#include "items/items.h"
#include "units/units.h"
#include "models/models.h"
#include "models/model_definitions.h"
#include "networking/network_game_globals.h"
#include "network_campaign.h"
#include "network_distributed.h"
#include <string.h>

struct campaign_object_pose
{
	long round;
	unsigned long seed;
	long object_index, parent_index;
	real scale;
	real body, shield;
	unsigned long visual_flags, unit_flags;
	word destroyed_regions;
	byte region_damage[MAXIMUM_REGIONS_PER_OBJECT];
	real_point3d position;
	real_vector3d forward, up;
	short parent_node;
	byte visible, attachment; /* 0 detached, 1 generic, 2 inventory/vehicle seat */
	byte permutations[MAXIMUM_REGIONS_PER_OBJECT];
};
static struct campaign_object_pose previous[MAXIMUM_TRACKED_OBJECTS];
static boolean valid[MAXIMUM_TRACKED_OBJECTS], force_refresh;
#define CAMPAIGN_VISUAL_FLAGS (FLAG(_object_no_collisions_bit) | FLAG(_object_shadowless_bit) | FLAG(_object_movie_star_bit))
#define CAMPAIGN_UNIT_FLAGS (FLAG(_unit_suspended_bit) | FLAG(_unit_not_enterable_by_player_bit) | FLAG(_unit_impervious_bit))

word network_campaign_objects_size(void) { return sizeof(struct campaign_object_pose); }
void network_campaign_objects_reset(void) { memset(valid, 0, sizeof(valid)); force_refresh = TRUE; }

static boolean managed_attachment(struct object_datum const *object)
{
	if (TEST_FLAG(_object_mask_unit, object->object.type) &&
		((struct unit_datum const *)object)->unit.parent_seat_index != NONE) return TRUE;
	return TEST_FLAG(_object_mask_item, object->object.type) &&
		TEST_FLAG(((struct item_datum const *)object)->item.flags, _item_attached_to_unit_bit);
}

void network_campaign_objects_tick(void)
{
	struct object_iterator iterator;
	struct { struct distributed_message_header header;
		struct campaign_object_pose entries[RELIABLE_ENTRIES(struct campaign_object_pose)]; } message;
	short count = 0;
	boolean refresh;
	if (!network_campaign_playing() || game_connection() != _game_connection_network_server ||
		(!force_refresh && game_time_get() % 3)) return;
	refresh = force_refresh || game_time_get() % (3 * TICKS_PER_SECOND) == 0;
	force_refresh = FALSE;
	object_iterator_new(&iterator, _object_mask_unit | _object_mask_item | _object_mask_scenery |
		_object_mask_device | FLAG(_object_type_sound_scenery), 0);
	while (object_iterator_next(&iterator))
	{
		struct object_datum *object = object_get(iterator.index);
		struct campaign_object_pose pose;
		long slot = DATUM_INDEX_TO_ABSOLUTE_INDEX(iterator.index);
		if (slot < 0 || slot >= MAXIMUM_TRACKED_OBJECTS) continue;
		memset(&pose, 0, sizeof(pose));
		pose.round = network_game_get_number_of_games_played();
		pose.seed = network_game_get_random_seed();
		pose.object_index = iterator.index;
		pose.scale = object->object.scale;
		pose.body = object->object.body_vitality;
		pose.shield = object->object.shield_vitality;
		pose.visual_flags = object->object.flags & CAMPAIGN_VISUAL_FLAGS;
		if (TEST_FLAG(_object_mask_unit, object->object.type))
			pose.unit_flags = ((struct unit_datum *)object)->unit.flags & CAMPAIGN_UNIT_FLAGS;
		pose.destroyed_regions = object->object.regions_destroyed_flags;
		memcpy(pose.region_damage, object->object.region_damage, sizeof(pose.region_damage));
		pose.visible = !TEST_FLAG(object->object.flags, _object_invisible_bit);
		pose.parent_index = object->object.parent_object_index;
		pose.parent_node = object->object.parent_node_index;
		pose.attachment = managed_attachment(object) ? 2 : pose.parent_index != NONE ? 1 : 0;
		/* Only a generic attachment needs a local transform. Keeping ordinary
		 * world transforms zero avoids resending every moving object's metadata. */
		if (pose.attachment == 1)
		{
			pose.position = object->object.position;
			pose.forward = object->object.forward;
			pose.up = object->object.up;
		}
		memcpy(pose.permutations, object->object.region_permutations, sizeof(pose.permutations));
		if (!refresh && valid[slot] && !memcmp(&pose, &previous[slot], sizeof(pose))) continue;
		previous[slot] = pose;
		valid[slot] = TRUE;
		message.entries[count++] = pose;
		if (count == NUMBEROF(message.entries))
		{
			distributed_send(&message, _distributed_message_campaign_objects, count,
				sizeof(message.header) + count * sizeof(pose), _distributed_to_clients_reliably);
			count = 0;
		}
	}
	if (count) distributed_send(&message, _distributed_message_campaign_objects, count,
		sizeof(message.header) + count * sizeof(message.entries[0]), _distributed_to_clients_reliably);
}

static boolean parent_valid(long child, long parent, short node)
{
	long depth;
	if (!network_objects_client_has(parent) || !object_try_and_get(parent) || !object_has_node(parent, node)) return FALSE;
	for (depth = 0; parent != NONE && depth < 128; depth++)
	{
		struct object_datum *object;
		if (parent == child || !(object = object_try_and_get(parent))) return FALSE;
		parent = object->object.parent_object_index;
	}
	return parent == NONE;
}

void network_campaign_objects_receive(void const *entries, short count)
{
	short index;
	if (!network_campaign_client()) return;
	for (index = 0; index < count; index++)
	{
		struct campaign_object_pose pose;
		struct object_datum *object;
		long model_index;
		struct model *model;
		short region;
		real_vector3d forward, up;
		memcpy(&pose, (byte const *)entries + index * sizeof(pose), sizeof(pose));
		if (pose.round != network_game_get_number_of_games_played() ||
			pose.seed != (unsigned long)network_game_get_random_seed() ||
			!distributed_object_index_valid(pose.object_index) || !network_objects_client_has(pose.object_index) ||
			!(object = object_try_and_get(pose.object_index)) || pose.visible > 1 || pose.attachment > 2 ||
			!(pose.scale >= 0.0f && pose.scale <= 100.0f) ||
			!(pose.body >= -1000.f && pose.body <= 1000.f) || !(pose.shield >= -1000.f && pose.shield <= 1000.f) ||
			(pose.visual_flags & ~CAMPAIGN_VISUAL_FLAGS) || (pose.unit_flags & ~CAMPAIGN_UNIT_FLAGS)) continue;
		if (pose.attachment == 1 && (!parent_valid(pose.object_index, pose.parent_index, pose.parent_node) ||
			!distributed_transform_valid(&pose.position, &pose.forward, &pose.up, NULL, NULL, &forward, &up))) continue;
		if (pose.attachment == 0 && pose.parent_index != NONE) continue;
		if (pose.attachment != 2 && !managed_attachment(object))
		{
			if (object->object.parent_object_index != NONE &&
				(object->object.parent_object_index != pose.parent_index || object->object.parent_node_index != pose.parent_node))
				object_detach(pose.object_index);
			if (pose.attachment == 1)
			{
				if (object->object.parent_object_index == NONE)
					object_attach_to_node(pose.parent_index, pose.object_index, pose.parent_node);
				object->object.position = pose.position;
				object->object.forward = forward;
				object->object.up = up;
			}
		}
		if (object->object.scale != pose.scale) objects_scripting_set_scale(pose.object_index, pose.scale, 3);
		/* Player health already has its own per-tick authority stream. */
		if (!TEST_FLAG(_object_mask_unit, object->object.type) || ((struct unit_datum *)object)->unit.player_index == NONE)
		{
			object->object.body_vitality = pose.body;
			object->object.shield_vitality = pose.shield;
		}
		object->object.flags = (object->object.flags & ~CAMPAIGN_VISUAL_FLAGS) | pose.visual_flags;
		if (TEST_FLAG(_object_mask_unit, object->object.type))
		{
			struct unit_datum *unit = (struct unit_datum *)object;
			unit->unit.flags = (unit->unit.flags & ~CAMPAIGN_UNIT_FLAGS) | pose.unit_flags;
		}
		object->object.regions_destroyed_flags = pose.destroyed_regions;
		memcpy(object->object.region_damage, pose.region_damage, sizeof(pose.region_damage));
		if (TEST_FLAG(object->object.flags, _object_invisible_bit) == pose.visible)
			object_set_visibility(pose.object_index, pose.visible);
		model_index = object_definition_get(object->definition_index)->object.model.index;
		model = model_index != NONE ? model_definition_get(model_index) : NULL;
		for (region = 0; model && region < model->regions.count && region < MAXIMUM_REGIONS_PER_OBJECT; region++)
		{
			struct model_region *definition = TAG_BLOCK_GET_ELEMENT(&model->regions, region, struct model_region);
			if (pose.permutations[region] == (byte)NONE || pose.permutations[region] < definition->permutations.count)
				object->object.region_permutations[region] = pose.permutations[region];
		}
	}
}
