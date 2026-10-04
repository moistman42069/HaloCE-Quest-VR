# Game files & versions

Open **Game files & versions** in either launcher, including before first import.

1. **Import ISO / XISO** accepts one or more locally supplied Xbox disc images.
2. **Import / scan a folder** uses Android's folder picker. Select a maps folder,
   an extracted game's root, or a parent containing extracted game roots/images.
3. Alternatively put images or folders containing `maps` in the displayed
   `game-versions/inbox` folder, then choose **Scan inbox**. Scanning is shallow;
   a `maps` folder directly in the inbox also works. Source files are retained.
4. Select **Use** beside a detected set. **Selected** identifies the active set.
   **Rename** changes a personal label; it does not change detected identity.

Selection applies at the next game launch. Quit to the launcher before switching.
Existing data remains selectable as **Existing game data**. There is no need to
move, overwrite or re-import the original installation. Each new set uses its
own maps, saves and config; current settings are copied once at import. Existing
progress remains with its original set. Switching back restores access to it.
Mobile touch/controller preferences remain app-wide. The two APKs have separate
app storage unless the VR installation already uses its supported shared root.

## What detection means

Imports read actual Xbox v5 cache headers: PAL `01.01.14.2342` and NTSC
`01.10.12.2276` / `01.08.15.1749`. The set lists detected region/build(s), hashes
every map and computes a combined SHA-256 fingerprint at import. Equal sets
deduplicate. Mods or manual file edits can change those bytes afterward; use
Game data & compatibility to read current headers and recompute fingerprints.
UI must be a recognized menu cache; unsupported cache builds/types are rejected
for managed imports. Resource files (bitmaps/sounds/loc) are hashed separately.
Unknown custom content remains the existing experimental content path.

Header recognition is not authentication of the complete map or a full-disc
integrity check. There is no verified Original/Rev1/Rev2 hash database in this
project; those disc labels remain **unverified**, even if a filename says Rev2.
You can add your own label while retaining the detected build/fingerprint.
PAL normalization is automatic in the existing engine.

## Multiplayer assistance and limits

If a PvP listing names a supported map missing from the selected set, the browser
offers other imported sets containing it. You choose the set before joining.
If none is installed it explains which map is needed. It never fabricates a
required disc revision: the current directory advertises a map and network
version, not authoritative disc revisions or per-map content hashes.

Native networking accepts reviewed distributed versions 9-11; campaign needs a
matching CE01 project build and matching mission/resource content. Retail PC,
Custom Edition, original Xbox and MCC network protocols are different. Changing
data sets cannot convert these protocols or solve NAT, closed/full hosts or
expired invitations. A host can rotate to maps not named in its earlier listing.

## Storage, interruption and recovery

The launcher displays the actual inbox path. Managed sets live under the same
base as existing game data, in `game-versions/p-<id>`. `profile.properties` stores
detected identity and SHA-256 entries; `active-data.txt` is the atomic selection
marker used by both Java and native startup. Selected saves live under that
set's `save` directory. Existing saves/config are never moved.

Imports use hidden-from-selection `partial-*` staging, validate/hash before
finalization, then rename the complete set. Cancelled/failed imports clean their
own staging folder; other complete imports in a batch remain available. An OS
process kill can leave an inert `partial-*` folder; it is never selectable.
No original ISO/extracted folder is deleted. Limits: 64 installed sets, 512 map
files and 12 GiB per managed set; the ISO extractor allows 4096 entries per directory table.
Additional space is needed for the copied maps during import. Unreadable or
invalid active selections stop launch and direct you to choose a complete set.

Back up the entire data root, including `game-versions`, to preserve all sets and
saves. The project updater preserves these files. Uninstalling an Android app
can remove its app-specific storage; updating with the signed APK preserves it.

Imports and fingerprints stay on-device. Logs may include your chosen labels,
paths, map identities and network invitations; review logs before sharing them.
No game data is included in the project, APKs or source archives.

## ISO/XISO troubleshooting (test19)

The Android importer recognizes plain XDVDFS images and the three whole-disc
partition offsets used by extract-xiso. It accepts deep valid directory trees,
case-insensitive maps/UI names and 64-bit file offsets. Synthetic fixtures cover
all four layouts and data beyond 4 GiB. This is not a guarantee for every disc,
mod or transfer provider; managed imports still validate actual cache headers.

Copy the complete image to local Downloads before importing. Compare byte size
and SHA-256 with the source if it works on another device. Unpack ZIP/7z/RAR
containers and merge split parts before selecting an image; selecting only one
part cannot work. A readable original-Xbox Halo image or an extracted maps folder
is required. PC/MCC disc containers are different formats. Cyclic directory
entries, duplicate names, unsafe paths, damaged volume headers and out-of-file
extents are rejected. Import never downloads game data or bypasses integrity checks.
