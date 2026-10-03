# Continuing between local VS Code and cloud agents

Canonical public repository: `https://github.com/moistman42069/HaloCE-Quest-VR`.
Default branch: `main`. The private predecessor retains history/keys/evidence;
do not replace the current public source with its older branch defaults.

## Start

```sh
git clone https://github.com/moistman42069/HaloCE-Quest-VR.git
cd HaloCE-Quest-VR
git status --short --branch
git pull --ff-only
git switch -c feature/descriptive-name
```

Read CLAUDE.md, docs/CURRENT-STATE.md, docs/RELEASE-PROVENANCE.md and
CONTRIBUTING.md. Current code contains VR test13a and the flat path; the shipped
flat binary remains test13. No private chat history is needed. Historical TEST*
documents explain earlier decisions but may describe superseded defaults.

On the maintainer's Windows workstation, use a D: checkout and keep builds,
caches and scratch files on D:. Cloud/Linux paths are environment-specific.
Never copy a personal absolute path into public documentation.

## Handoff

Commit intended changes and push the feature branch. Record the exact changes,
build/check commands and results, unresolved issues, next steps and artifact
hashes in CURRENT-STATE or a linked dated note. Preserve unrelated user work.
Use GitHub noreply commit metadata. Do not commit game data, signing keys,
credentials, logs containing host invitations or personal recordings.

Runtime acceptance comes from device results. A clean build is not a headset,
phone or paired multiplayer result. Keep the shipped APK/source identities
separate from later documentation commits. The project signing key remains
private; ordinary cloud debug builds cannot update signed release installations.

## Suggested resume instruction

> Continue from this repository's current main branch. Read CLAUDE.md,
> docs/CURRENT-STATE.md, docs/RELEASE-PROVENANCE.md and CONTRIBUTING.md first.
> Inspect the current code and worktree, preserve existing work, and state the
> next concrete change supported by the latest issue/device evidence. Maintain
> both VR and flat paths; build flavors serially. Update the checkpoint with
> exact results and remaining device checks. Do not infer acceptance from builds
> or publish/install/launch without the relevant user authorization.
