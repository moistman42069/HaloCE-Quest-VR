# Test14: co-op NPC presentation candidate

## User evidence and delivery hold ? 2026-10-03

The owner confirmed Quest/flat co-op connectivity and that full VR body movement is visible on the flat Android partner. NPCs instead slide without walking; one appeared stuck in a falling pose. The private 09:47 Quest log explicitly identifies test13, records campaign client barriers and avatar capability negotiation, and ends normally. Sampled frames from the 46-second recording show the a10 corridor and remote player; the recording is not a host-side trace and cannot identify every NPC state. One transparent-geometry capacity warning appears; no source change for that separate warning is included without further evidence.

The public source repo remains available. The initial test13a GitHub release was removed at the owner's request. **Do not publish new APKs or create another release until the owner tests both candidate APKs and approves publication.** Keep raw logs, recordings, invites, workstation details and signing keys private.

## Source findings

1. Host `actor_unit_control` produces native movement/aim/fire inputs and marks units actively controlled through the AI lifecycle. Client `network_campaign_actors_receive` previously called only `unit_control`. A client-created NPC has no local actor/player, and `unit_control` does not mark it actively controlled. The next `unit_update` therefore zeroed its throttle/control flags before `biped_update_moving` chose a walking animation. Network transforms still moved the object: this directly explains sliding with idle animation.
2. `network_objects_handle_states` discarded an entire snapshot when its position/orientation was within tolerance. That also discarded changed velocities and the host's rest bit. `biped_update_dead` chooses dying-airborne from local airborne ticks; an at-rest dead biped with ignore-translation can skip its physics update. Ignoring a host rest transition can retain stale airborne presentation. This is a concrete synchronization defect and a plausible contributor to the reported falling pose; footage alone does not prove it was the only cause.

## Changes

- A validated host NPC control record grants native active-control ownership on the client. Player units and dead units are excluded; no local AI or independent mission logic is created.
- The lease expires after two seconds of simulation time without valid host controls, on death, lost ownership, or time rewind. Expiry clears movement/fire and borrowed control flags. Round/seed, object salt/ownership, range, vector and packet-order checks remain. Seen records survive lease expiry until reset so a restored checkpoint cannot retain borrowed flags from an earlier lease.
- Map/barrier reset releases borrowed ownership. Valid subsequent host packets reacquire it. Controls are not repeatedly applied as synthetic new button presses.
- For campaign client NPC bipeds only, host velocity/rest updates apply even within positional tolerance. Resting bipeds take the exact host position and clear stale airborne ticks/flags; native biped physics establishes that its rest flag implies grounded. Moving actors still use the existing prediction/interpolation path.
- AI one-shot animation impulses now have reliable campaign message 39 (24-byte records, round/seed/object/enum/alignment validation). Native eligibility remains in charge; uninitialized local animation graphs are rejected safely. Events captured before save/BSP barriers remain queued; restored timelines/new maps clear them. Old clients ignore the added message; test both peers on test14 for the complete behavior.
- Unarmed campaign vehicle passengers now receive inventory/seat records. Previously the inventory optimization could exclude them despite that record owning seat replication.
- The supplied log also records a missing competitive pause tag in the campaign cache. Co-op now selects the authored campaign pause/settings widget through the network menu route. Its widgets/error dialogs do not freeze a single peer's simulation or sound. Checkpoint/restart authority remains with the host; leaving quits the session.
- Competitive v9/v10 packets, existing campaign CE01 layouts, player movement, VR avatar packets, local body/finger/grip behavior and Legs + Arms defaults are unchanged. The new campaign-only optional event is appended after avatar IDs, not inserted into existing IDs.
- Both flavors use version 1.0-test14 / code 15. New periodic `campaign actors:` log counters identify applied host controls and expired leases without logging each NPC/tick.

## Build / acceptance

See [COOP-COMPATIBILITY-AUDIT.md](COOP-COMPATIBILITY-AUDIT.md) for the review matrix and executable regression checks. Build and packaging results will be recorded in TEST14-DELIVERY.md after both flavors complete. No device install, game launch, new runtime result or public APK upload is implied by compilation.

## Requested paired-device check

Install test14 on both peers. Repeat the a10 corridor on both host/client assignments (Quest host and flat host). Compare marine/crew/enemy walking, starts/stops, turns, firing, deaths and bodies landing. Check doors, checkpoint recovery, both-dead recovery and a BSP transition if possible. Confirm the already-working remote VR body and room-scale legs remain correct. Preserve both Download/HaloCE launch logs and short recordings for any remaining issue. Broader full-campaign progression and all phone configurations remain unaccepted.
