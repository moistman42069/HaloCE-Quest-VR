# Agent and contributor continuation

Canonical repository: `moistman42069/HaloCE-Quest-VR`, default branch `main`.
Read docs/CURRENT-STATE.md, docs/RELEASE-PROVENANCE-1.0.0.md, CONTRIBUTING.md,
and relevant player/architecture/protocol documents before changes.

Current candidate: **test18 / Android code 19**, branch `release-1.0.0`.
Read docs/TEST18-PROGRESS.md and docs/TEST18-DELIVERY.md. Publication is ON HOLD:
the owner now requires both APKs in chat, then device testing, then a new explicit
instruction to resume the 1.0 plan. Do not create/upload/publish a GitHub release
or tag for this candidate. Existing public test14 must remain untouched.
The prepared 1.0 notes/template and updater support remain pending; they are not
evidence that 1.0 exists. Final 1.0 will need a version code above candidate 19.

Preserve accepted VR animation handoff, Legs + Arms, room-scale legs, fingers,
contact/grip, online native melee, Safe VR geometry and Normal flat geometry.
Keep the flat touch/controller, co-op/NPC/avatar, logging, browser and managed
set implementations. Co-op is two-player for concrete lifecycle/recovery reasons;
128 PvP slots do not establish 128-player campaign or Quest hosting performance.
Do not invent disc-revision labels, verified content matching, directories or
headset acceptance. Record code, automated checks and device evidence separately.

Keep all new local work/builds on D: on the maintainer's Windows machine. Other
systems use a writable clone. Check status and read continuation docs first.
Build VR/flat serially; native staging is shared. Preserve each APK before a
flavor switch. No game install/launch or unrelated upstream push without a
corresponding instruction. Use GitHub noreply authors; never publish private
history, personal paths/emails, keys, game assets, raw logs/media or invitations.
Required third-party license notices remain intact.

Every future release must have self-contained notes in the nine-section order
in docs/RELEASE-TEMPLATE.md, installation and APK download links first. Upload
only the two APKs plus updater compatibility metadata unless another asset has
a concrete purpose. Preserve existing releases. Version names, monotonically
increasing Android codes, stable tags, APK names and UpdatePolicy must agree.
Older test updaters require one manual install of 1.0; do not disguise that
limitation with fake compatibility metadata or duplicate legacy releases.
