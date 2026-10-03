# Optional network VR avatars (test13)

Both APKs implement the receiver/renderer. Quest additionally publishes its
solved avatar; flat Android observers do not need OpenXR. Local body visibility
does not hide the avatar from peers. The complete biped palette is captured
before the local head/shoulder/torso filters. Foot planting and inferred torso
follow the local solver; head direction, hand position and wrist orientation
follow tracking. Fresh first-person contact/support-grip targets are reused.
The stock biped has 19 nodes and no individual finger bones: this does not add
finger geometry or promise first-person finger detail on the remote model.

## Compatibility

- Requires a supporting host and supporting observer. Co-op and PvP use the
  same optional extension; stock PvP versions/packets remain 9/10 as before.
- Message 38 offers capability version 1 with magic 0x56525031, round, seed and
  nonce. Client responds; host acknowledges. Poses (37) start only after this
  exchange. A client connected to an old host sends no extension traffic.
- Host offers repeat every two seconds, lease expires after six. Old clients
  ignore the unknown offer. The reviewed upstream v10 handler explicitly
  rejects IDs outside its enum and processes sibling batch messages separately:
  [upstream decoder](https://github.com/ChupathingyCE/chupathingyce/blob/main/port/linux/game/network_distributed.c).
- Poses are relayed only to capable viewers for whom the host's existing player
  visibility predicate passes. Older clients continue to see stock animation.
  This cannot make an unmodified public server render or relay new VR poses.
- On-map/reset/restart state is cleared. Capability is bound to the machine's
  current salted player identity; a replaced player must negotiate again.

## Bounds and rendering

Up to 64 nodes, 64-byte entries; complete snapshots assemble across datagram
chunks before becoming visible. Per-entry magic/round/seed, object identity,
owning player, node/count, scale, finite position and orthogonal axes are checked.
The player's unit must be the same living, unattached biped and have the same
node count. The host verifies the sender owns that player. Local players cannot
be overwritten by remote pose records. Stale sequence numbers are rejected.

15 Hz sending, approximately 18.2 KB/s of joint data for a 19-node avatar per
visible supporting recipient, plus transport headers. Positions are relative
to the simulated unit root. Observer interpolation uses quaternion rotations
and positional blending; loss begins fading to stock after 250 ms and completes
at 500 ms. Held-weapon rendering follows the engine's existing parent-node
attachment using a render-only transform. Shadows use the same remote palette.

No simulation nodes, hitboxes, shot origins, damage, collision, input or movement
rules are changed. Flat input/controls remain the existing touch/gamepad path.
Three tracked devices infer torso/legs; there are no elbow/hip/foot trackers.
Seated/dead/non-biped or mismatched rigs retain stock observer animation.

Logs report negotiation, the first published unit, and the first complete
received avatar. Compile/package checks do not establish network runtime success.
Pending owner checks: two Quest clients; Quest plus flat observer; supporting
PvP host with supporting and old clients; disconnect/reconnect, death/respawn,
checkpoint/map transitions, grip alignment and packet-loss fallback.
