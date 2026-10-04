# Credits and licenses

This fork depends on substantial prior work. Credits distinguish code foundations, reference material and related projects; they do not imply endorsement or that all features of another project are included.

| Project / people | Contribution or relationship |
| --- | --- |
| Bungie and the original Halo team; Microsoft and the respective rights holders | Original Halo: Combat Evolved game, art, audio, story and technology. Game maps/data are supplied by the player, not licensed by this repository's source license. |
| [punpckhdq/halo](https://github.com/punpckhdq/halo), [bnunu/halo-1](https://github.com/bnunu/halo-1) and their contributors | Xbox Halo CE decompilation foundation. The inherited port identifies build 2342 (`cachebeta.exe`) as its decompilation target. |
| [bnunu/halo-ce-universal](https://github.com/bnunu/halo-ce-universal), [cybersecurity/halo-ce-universal](https://github.com/cybersecurity/halo-ce-universal) and contributors | Native Linux/Windows/Android port, guest/host architecture, renderer, networking, extraction/launcher and platform work inherited by this fork. |
| [astromaddie/HaloCE-VR](https://github.com/astromaddie/HaloCE-VR) / Madison | OpenXR VR foundation merged into the predecessor checkout as CC0: stereo rendering, tracked inputs, hand aiming, initial arm IK, scope, vehicles, room-scale, menus and related VR systems. |
| [moistman42069](https://github.com/moistman42069) and this fork's development/testing work | Quest adaptation and integration, body/finger/contact refinements, interaction/default changes, launcher/browser, campaign/avatar extensions, flat touch controls, logging, packaging and device feedback. See current-state for evidence and unfinished verification. |
| [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce) and the halo.milenko.org service maintainers | Compatible native-port directory and published invite/listing/announcement protocol used by the launcher. The service is independent of this fork. |
| [LivingFray/HaloCEVR](https://github.com/LivingFray/HaloCEVR) | Earlier original-PC VR conversion and room-scale design reference acknowledged by the inherited VR code. This Android project is a separate codebase/target; no exclusive or first-to-VR claim is made. |
| [rollingrock / FRIK](https://github.com/rollingrock/Fallout-4-VR-Body), [hai-vr / hvr-ik](https://github.com/hai-vr/hvr-ik), [Unity two-bone IK documentation](https://docs.unity3d.com/Packages/com.unity.animation.rigging@1.2/manual/constraints/TwoBoneIKConstraint.html) | Body/IK reference research for bend continuity, bounded reach, head/body priorities and target/hint separation. These were studied as references; the test13 refinements were implemented for Halo's own rig, without importing their code or foreign game bindings. |
| Players and bug reporters | Headset recordings, logs and feedback that guided menu, body, grip, finger and multiplayer changes. Private recordings/logs and identifying information are not published. |

## Bundled software and assets

The root [LICENSE.md](LICENSE.md) is the inherited CC0 dedication. It does not replace dependency licenses or grant rights to Halo game data/trademarks. Existing copyright/license headers are retained.

- **SDL3**: platform, input/audio/activity support; zlib license. Shipped dependency version is 3.4.16. [Notice](docs/licenses/SDL3-LICENSE.txt).
- **Khronos OpenXR SDK/loader**: VR API/loader, version 1.1.63. [License](docs/licenses/OpenXR-LICENSE).
- **musl** 1.2.5: guest C runtime; [copyright/license](docs/licenses/musl-COPYRIGHT). The vendored math subset has its own [notes](port/third_party/musl-math/README.md).
- **KCP**, **miniupnpc**, **Mbed TLS**, **tomlc17**, **stb**: retained [third-party sources/notices](port/third_party). Consult each component's LICENSE/README and file headers.
- **extract-xiso**: original work by in, with additional project contributors. Required acknowledgement: **This product includes software developed by in &lt;in@fishtank.com&gt;.** [Modified BSD license](port/third_party/extract-xiso/LICENSE.TXT). Extraction code retains that notice.
- **zlib** and **libtiff**: inherited compression/image libraries; notices remain in [zlib](source/memory/zlib/README) and [libtiff headers](source/bitmaps/libtiff/tiff.h).
- **Overpass** by Red Hat/Delve Withrington, **Newtown** by Roger White, and the port's respaced **OpenCE** title font: [font provenance and license files](port/assets/fonts/README.md). The release bundle includes their notices.
- **LLVM/Clang, Android SDK/NDK, Gradle, CMake, Ninja and Python** provide the build toolchain; they are not all bundled with the APKs.

The public repository begins with a privacy-clean current snapshot. Earlier private author metadata is not exposed. Public upstream links and retained file/license notices preserve attribution; this snapshot is not a claim that this fork wrote the inherited code.

## Test15 additions

Selected v10/v11 networking and gameplay changes are adapted from bnunu/cybersecurity halo-ce-universal contributors; pinned commits and integration boundaries are in [the upstream audit](docs/TEST15-UPSTREAM.md). Ordered static GPU uploads follow Andiweli's [HaloCE-Android-AAOS fix](https://github.com/Andiweli/HaloCE-Android-AAOS/commit/a88f25763b8a51335554ef02e613127ee92677d4). SnowyMouse's [Halo cache format documentation](https://gist.github.com/SnowyMouse/39168bddd597549038a35d78aee39513) (CC BY 3.0) informed header reporting; the recognition code is adapted for this launcher. Activision's official mobile control guides informed HUD usability only; no shooter code/art was imported. Launcher backgrounds are procedural original drawings, with no extracted Halo artwork bundled.

Test15 Android controller support retains SDL 3.4.16 mappings and Android input APIs. Local SDL changes are recorded under `port/android/patches`, including generic Android digital-only L2/R2 mapping and the existing clipboard-service guard. SDL copyright/license remains in the bundled third-party notices. Controller settings/navigation/visibility are project code.

## Test19 additions

Signed OpenCE lobby discovery and Ed25519/X25519 identity binding are adapted
from cybersecurity/halo-ce-universal build 84, principally commit
`c04765d7f49f49bda706a258826134ef41c566ca`. The stock Xbox widget integration is
project code. [Monocypher](https://monocypher.org/) by Loup Vaillant and its
contributors supplies the cryptographic primitives; complete licenses accompany
`port/third_party/monocypher` and the bundled notices. XboxDev/extract-xiso's
format handling and deep-tree warning informed the importer correction. Khronos
OpenGL ES and OpenXR specifications informed renderer-state and reticle-space
review. These references establish API/format behavior, not device acceptance.
