# stb_truetype

A TrueType font rasterizer in one C header, by Sean Barrett (RAD Game
Tools), public domain or MIT licensed, as the user chooses (see
`LICENSE`).

Upstream: https://github.com/nothings/stb, commit
2c980bb59875b0d32144a71867fbdebb2f77cd20 (`stb_truetype.h` v1.26), copied
unchanged.

The game's text is drawn with fonts from `port/assets/fonts`, rasterized
with it at the display's resolution (`port/linux/src/text_hires.c`); it
builds into the Linux, Windows and Android platform layers.

# stb_vorbis

An Ogg Vorbis decoder in one C file, by Sean Barrett, public domain or MIT
licensed, as the user chooses (the same `LICENSE`).

Upstream: https://github.com/nothings/stb, commit
f58f558c120e9b32c217290b80bad1a0729fbb2c (`stb_vorbis.c` v1.22), copied
unchanged (SHA-256
4c7cb2ff1f7011e9d67950446b7eb9ca044f2e464d76bfbb0b84dd2e23e65636).

Halo Custom Edition maps keep many sounds as Ogg Vorbis, which the Xbox's
sound system cannot play: the Custom Edition loader decodes them with it
and encodes them as Xbox ADPCM once, keeping the result beside the map
(`port/linux/game/custom_edition_sounds.c`).
