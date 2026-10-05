# PC and Steam Frame: feasibility (2026-10-05)

Phase after the Android builds. Nothing here changes the Quest or flat
Android builds.

## First, what is being asked

Community requests ask for "a PC port". Two different projects hide behind
that:

1. **Flat desktop** with this project's features (launcher, data manager,
   campaign co-op, browser). OpenCE already ships native flat Windows/Linux
   x86 (32-bit, OpenGL 4.5, SDL3) builds of the shared decomp. What this
   project adds there is mostly Android-side (the launcher is Java) or
   protocol-specific (CE01 co-op, network 11).
2. **PC VR** (SteamVR/Oculus link, Windows or Linux x86_64). This is the VR
   work of this project on a desktop.

The requesters should be asked which they mean before either is scoped.

## Facts that decide the architecture

- The game is a 32-bit x86 decomp on desktop (and an ARM64 guest on Android).
  **PC VR runtimes (SteamVR, Oculus, WMR) are 64-bit libraries; a 32-bit
  process cannot load them.** OpenCE PR #85 says the same.
- OpenCE PR #85 (**open**, by startupfoundry) adds OpenXR to the native
  **arm64 Linux** build for the **Steam Frame** (tested on Frame with SteamVR;
  Monado simulated). It renders single-pass multiview stereo, uses quad layers
  for HUD/menus and runtime-paced frames. It is not a Windows PCVR port. It
  depends on PR #71 (native arm64 Linux).
- This project's VR is split into an OpenXR **host** (`port/android/host/
  host_xr.c`, Android NativeActivity + GLES) and **guest** VR code
  (`port/linux/src/vr_frame.c`, `port/linux/game/vr_render.c`, `vr_menu.c`,
  shared with the flat game through `HALO_VR`). The guest asks the host for
  frames, poses and swapchain images through `halo_android_abi.h`; it does not
  call OpenXR itself.

## Likely architecture

| Target | Shape | Main work |
| --- | --- | --- |
| Steam Frame (arm64 Linux) | Build the guest natively for arm64 Linux (as PR #71/#85) and provide a Linux OpenXR **host** implementing the same ABI as `host_xr.c` (desktop GL or GLES context, SDL3 window) | A Linux host for `halo_android_abi.h`; input profile for the Frame's controllers (`frame[]` bindings already exist in `host_xr.c`); data paths and config outside Android storage |
| PC VR, Windows x86_64 | Either a **64-bit build** of the game (decomp pointer-size work: tag/data structures assume 32-bit) or an **out-of-process bridge**: the 32-bit game renders into shared textures; a 64-bit helper owns the OpenXR session and passes poses/input back | Bridge: shared-texture interop (D3D11/GL interop or Vulkan external memory), a low-latency pose channel, frame pacing across processes. 64-bit: large decomp audit |
| PC flat with project features | Port the Java launcher features to desktop (or reuse OpenCE's desktop UI) and keep CE01 co-op/network 11 compatibility | UI rewrite; protocol choice (see the upstream review) |

## Dependencies

OpenXR loader (desktop), a GL/Vulkan interop path for the bridge, SDL3,
desktop data-path handling for the game-data manager, and the owner's decision
on network version (11 vs upstream 16) for any desktop build meant to play with
Quest users.

## Risks

- The 32-bit vs 64-bit split is the biggest PC VR risk; a bridge adds latency
  and complexity, and 64-bit is a large audit.
- Android assumptions in the VR guest: GLES-only paths, sRGB write control,
  `glBlitFramebuffer` to swapchain images, the Quest touch layout and refresh
  rates, Android storage paths.
- Upstream PR #85 is open and moving; building on it now risks rework.
- Testing needs the hardware (Steam Frame, a PC VR headset). Nothing can be
  accepted without it.

## Staged plan

1. Ask requesters: flat desktop or PC VR, and which headset.
2. Steam Frame first (arm64, 64-bit, same OpenXR model): once PR #71/#85 settle
   upstream, write a Linux `host_xr` for this project's ABI and run the existing
   guest VR code on it. Re-use PR #85's runtime-paced timing and Frame
   bindings where compatible.
3. PC VR prototype through an out-of-process bridge on Linux x86_64 first
   (simpler interop), then Windows.
4. Decide the network version for desktop builds before any public release.
