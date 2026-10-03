/*
AUDIO_CODECS.H

Ogg Vorbis decoding and Xbox ADPCM encoding (audio_codecs.c), for the
Custom Edition loader, which converts the Ogg Vorbis sounds of Halo Custom
Edition maps into the Xbox ADPCM the game's sound system plays
(port/linux/game/custom_edition_cache.c).
*/

#ifndef __HALO_LINUX_AUDIO_CODECS_H
#define __HALO_LINUX_AUDIO_CODECS_H

/* Decodes the Ogg Vorbis stream `data` (`size` bytes) into 16-bit PCM of
`channels` channels (1 or 2; others are mixed down or doubled) at
`sample_rate` hertz (resampled when the stream's differs). Returns the
frame count, with the interleaved samples in *samples (free with free), or
-1 when the stream cannot be decoded. */
long halo_ogg_decode(const void *data, long size, int channels, long sample_rate, short **samples);

/* Encodes `frames` frames of interleaved 16-bit PCM of `channels` channels
(1 or 2) as Xbox ADPCM: blocks of 36 bytes a channel, 65 frames each (the
first in the block's header), the last padded with silence. Returns the byte count, with the encoded bytes in
*encoded (free with free), or 0 when out of memory. */
unsigned long halo_xbox_adpcm_encode(const short *samples, unsigned long frames, int channels,
	unsigned char **encoded);

/* frees what the two above returned. They allocate with the C library,
which the game's own free (its debug allocator's, cseries.h) must not be
given: callers in the game's sources free with this. NULL is ignored. */
void halo_audio_free(void *memory);

#endif
