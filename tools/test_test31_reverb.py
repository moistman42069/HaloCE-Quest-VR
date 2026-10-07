"""Compile the production optional room mixer; no device, game or packaging."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test31-reverb'
OUT.mkdir(parents=True, exist_ok=True)
source = (ROOT / 'port/linux/src/dsound_sdl.c').read_text()
prior = subprocess.check_output(['git', 'show', 'cfd1ff6c:port/linux/src/dsound_sdl.c'], cwd=ROOT, text=True)
xdk = (ROOT / 'port/include/xdk/xdk_pdb.h').read_text()
win32 = (ROOT / 'port/include/xdk/xdk_win32.h').read_text()
# Pull the real HRESULT definition; an invented mock constant cannot hide a missing SDK symbol.
invalid_argument = re.search(r'^#define E_INVALIDARG .*$', win32, re.M).group()
assert 'DSERR_INVALIDPARAM' not in source


def fn(text, name):
    m = re.search(r'^(?:static )?[\w *]+\b' + name + r'\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    i = text.index('{', m.start()) + 1
    depth = 1
    while depth:
        depth += (text[i] == '{') - (text[i] == '}')
        i += 1
    return text[m.start():i] + '\n'


# These accepted paths are intentionally outside this change.
for name in ('decode_adpcm', 'catmull_rom', 'voice_frame', 'spatialize',
             'voice_gains', 'audio_statistics_log'):
    assert fn(source, name) == fn(prior, name), name
assert '#define XBOX_ADPCM_BLOCK_SAMPLES 65' in source
assert 'config_' not in fn(source, 'mix') + fn(source, 'audio_callback')
assert 'reverb_initialize();' in fn(source, 'audio_start')
assert '"audio.reverb", _config_boolean, "false"' in (ROOT / 'port/linux/src/port_config.c').read_text()

types = '\n'.join(re.search(r'struct ' + n + r' \{.*?\n\};', xdk, re.S).group()
                  for n in ('_DSI3DL2OBSTRUCTION', '_DSI3DL2OCCLUSION', '_DSI3DL2BUFFER', '_DSI3DL2LISTENER'))
header = r'''
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>
typedef int BOOL;
typedef long LONG, HRESULT;
typedef unsigned long DWORD, ULONG;
typedef void *LPVOID, *LPDIRECTSOUND, *LPDIRECTSOUNDSTREAM;
typedef void (*LPFNXMEDIAOBJECTCALLBACK)(void);
typedef struct { void *unused; } IDirectSoundStream;
typedef struct { void *unused; } XMEDIAPACKET;
#define TRUE 1
#define FALSE 0
#define WINAPI
#define DSBVOLUME_MIN -10000
#define DS_OK 0
#define DS3DMODE_DISABLE 2
#define DS3DMODE_HEADRELATIVE 1
static int mutex_depth;
typedef int pthread_mutex_t;
#define PTHREAD_MUTEX_INITIALIZER 0
static void pthread_mutex_lock(pthread_mutex_t *p){(void)p;assert(!mutex_depth);mutex_depth++;}
static void pthread_mutex_unlock(pthread_mutex_t *p){(void)p;assert(mutex_depth);mutex_depth--;}
static unsigned long config_changes(void){assert(!mutex_depth);return 0;}
static double config_real(const char *p){assert(!mutex_depth);(void)p;return 1;}
static int config_boolean(const char *p){assert(!mutex_depth);(void)p;return 0;}
static void platform_log(const char *p,...){(void)p;}
''' + invalid_argument + '\n' + types + r'''
typedef struct _DSI3DL2LISTENER DSI3DL2LISTENER;
typedef const DSI3DL2LISTENER *LPCDSI3DL2LISTENER;
typedef struct _DSI3DL2BUFFER DSI3DL2BUFFER;
typedef const DSI3DL2BUFFER *LPCDSI3DL2BUFFER;
'''

# The entire production mixer, including real data structures and DSP.
body = source[source.index('#define OUTPUT_RATE'):source.index('/* ---------- output */')]
body += fn(source, 'IDirectSound_SetI3DL2Listener')
body += r'''
#define STREAM_SETTER(body) struct sdl_stream *record=(struct sdl_stream *)stream; \
 pthread_mutex_lock(&mixer_lock); body; pthread_mutex_unlock(&mixer_lock); return DS_OK;
'''
body += fn(source, 'IDirectSoundStream_SetI3DL2Source')
body += fn(prior, 'mix_voice').replace('mix_voice(', 'baseline_mix_voice(')
body += fn(prior, 'mix').replace('mix(', 'baseline_mix(').replace('mix_voice(', 'baseline_mix_voice(')

tests = r'''
static short samples[4096 * 2];
static float out[2048], expected[2048];
static void stream_init(struct sdl_stream *s, int channels, int spatial){
 memset(s,0,sizeof(*s));s->channels=channels;s->sample_rate=22050;s->frequency=30000;
 s->volume=0.7f;s->mix_left=0.6f;s->mix_right=0.8f;s->i3dl2_gain=1;
 s->minimum_distance=1;s->maximum_distance=100;s->position[0]=2;s->position[2]=4;
 s->has_3d=spatial;s->packet_count=2;
 for(int i=0;i<2;i++){
  s->packets[i].samples=samples+i*2048*channels;s->packets[i].frames=2048;
 }
}
static DSI3DL2LISTENER room(void){
 DSI3DL2LISTENER p={-1000,-100,0,0.7f,0.7f,-700,0.007f,0,0.011f,100,100,5000};return p;
}
static void finite_output(int frames){for(int i=0;i<frames*2;i++)assert(isfinite(out[i]) && fabsf(out[i])<=1.0f);}
static double energy(const float *p,int n){double e=0;for(int i=0;i<n;i++)e+=p[i]*p[i];return e;}
static void reset_room(int enabled){
 memset(&reverb,0,sizeof(reverb));reverb_enabled=enabled;master_volume=1;
 DSI3DL2LISTENER p=room();assert(IDirectSound_SetI3DL2Listener(NULL,&p,0)==DS_OK);
 reverb_initialize();
}
static void test_dry_identity(void){
 for(int i=0;i<4096*2;i++) samples[i]=(short)(sin(i*0.113)*14000);
 for(int spatial=0;spatial<2;spatial++)for(int channels=1;channels<=2;channels++){
  struct sdl_stream old,new;stream_init(&old,channels,spatial);new=old;reset_room(0);
  for(int block=0;block<8;block++){
   if(block==2){old.volume=new.volume=0.2f;old.position[2]=new.position[2]=3;}
   streams=&old;baseline_mix(expected,1024);streams=&new;mix(out,1024);
   assert(!memcmp(out,expected,sizeof(out)));
   assert(old.cursor==new.cursor && old.packets[0].finished==new.packets[0].finished);
  }
 }
 streams=NULL;puts("PASS: mono/stereo, 2D/3D dry mixer is byte-identical, including packet boundaries and gain ramps");
}
static void test_impulse_toggle(void){
 float input[1024]={0};double first=0,tail=0;
 reset_room(1);input[0]=0.2f;
 for(int i=0;i<230;i++){
  memset(out,0,sizeof(out));reverb_process(input,out,1024,1,1);finite_output(1024);
  if(i<10)first+=energy(out,2048);if(i>210)tail+=energy(out,2048);
  memset(input,0,sizeof(input));
 }
 assert(first>1e-7 && tail<first*0.001);
 input[0]=0.2f;memset(out,0,sizeof(out));reverb_process(input,out,1024,1,0);
 assert(energy(out,2048)==0); /* master mute applies to existing tails too */
 for(int i=0;i<5;i++){memset(out,0,sizeof(out));reverb_process(input,out,1024,0,1);}
 assert(reverb.level==0);reverb_clear();assert(reverb.silent && !reverb.fade);
 for(int i=0;i<REVERB_DELAY_SIZE;i++)assert(reverb.delay[i]==0);
 for(int i=0;i<REVERB_LINES;i++)for(int j=0;j<REVERB_LINE_SIZE;j++)assert(reverb.lines[i][j]==0);
 streams=NULL;reverb_enabled=0;mix(out,1024);assert(energy(out,2048)==0);
 puts("PASS: finite impulse response decays, live mute silences tails, disable clears buffers and stops DSP");
}
static void test_parameters(void){
 DSI3DL2LISTENER p=room();
 p.flDecayTime=NAN;p.flDensity=INFINITY;p.flHFReference=-INFINITY;
 p.flReflectionsDelay=NAN;p.flReverbDelay=INFINITY;p.flRoomRolloffFactor=NAN;
 p.flDiffusion=NAN;p.flDecayHFRatio=NAN;p.lRoom=INT32_MAX;p.lRoomHF=INT32_MIN;
 p.lReflections=INT32_MAX;p.lReverb=INT32_MAX;
 assert(IDirectSound_SetI3DL2Listener(NULL,NULL,0)==E_INVALIDARG);
 assert(IDirectSound_SetI3DL2Listener(NULL,&p,0)==DS_OK);
 reverb_parameters_set(&reverb.to,&environment);
 for(int i=0;i<REVERB_LINES;i++){
  assert(reverb.to.lengths[i]>0 && reverb.to.lengths[i]<REVERB_LINE_SIZE);
  assert(isfinite(reverb.to.feedback[i]) && reverb.to.feedback[i]>=0 && reverb.to.feedback[i]<1);
  assert(isfinite(reverb.to.damping[i]) && reverb.to.damping[i]>=0 && reverb.to.damping[i]<1);
 }
 for(int i=0;i<REVERB_TAPS;i++)assert(reverb.to.taps[i]<REVERB_DELAY_SIZE);
 assert(reverb.to.late_delay<REVERB_DELAY_SIZE);
 p=room();p.flDecayTime=20;p.flDecayHFRatio=2;p.flDensity=100;
 p.flReflectionsDelay=0.3f;p.flReverbDelay=0.1f;p.flHFReference=20;
 IDirectSound_SetI3DL2Listener(NULL,&p,0);reverb_parameters_set(&reverb.to,&environment);
 assert(reverb.to.late_delay==19200);
 for(int i=0;i<REVERB_TAPS;i++)assert(reverb.to.taps[i]<REVERB_DELAY_SIZE);
 struct sdl_stream s;stream_init(&s,1,1);
 DSI3DL2BUFFER b={0};b.Obstruction.flLFRatio=NAN;b.Occlusion.flLFRatio=INFINITY;
 b.Obstruction.lHFLevel=INT32_MIN;b.Occlusion.lHFLevel=INT32_MIN;b.flRoomRolloffFactor=NAN;
 b.lDirect=INT32_MAX;b.lRoom=INT32_MAX;b.lRoomHF=INT32_MIN;b.lDirectHF=INT32_MIN;
 assert(IDirectSoundStream_SetI3DL2Source(&s,NULL,0)==E_INVALIDARG);
 assert(IDirectSoundStream_SetI3DL2Source(&s,&b,0)==DS_OK);
 assert(isfinite(s.i3dl2_gain) && isfinite(s.room_rolloff_factor));
 puts("PASS: listener/source finite bounds, maximum delays and null inputs under ASan/UBSan");
}
static void test_routing(void){
 struct sdl_stream s;stream_init(&s,1,0);reset_room(1);
 float a,b,c;voice_room_gains(&s,&a,&b,&c);assert(!a&&!b&&!c);
 s.has_3d=1;s.direct=-100;s.direct_hf=-3000;s.room=-200;s.room_hf=-1000;
 voice_room_gains(&s,&a,&b,&c);assert(a>0 && b>0 && c>0);
 s.mode=DS3DMODE_DISABLE;voice_room_gains(&s,&a,&b,&c);assert(!a&&!b&&!c);
 s.mode=0;reverb_enabled=0;voice_room_gains(&s,&a,&b,&c);assert(!a&&!b&&!c);
 reset_room(1);memset(samples,0,sizeof(samples));samples[0]=18000;stream_init(&s,1,1);
 streams=&s;mix(out,1024);finite_output(1024);
 DSI3DL2LISTENER p=room();p.flDecayTime=2;IDirectSound_SetI3DL2Listener(NULL,&p,0);
 mix(out,1024);assert(reverb.fade>0 && reverb.fade<REVERB_FADE_FRAMES);
 reverb_enabled=0;for(int i=0;i<5;i++){mix(out,1024);finite_output(1024);}
 assert(reverb.silent && reverb.level==0);assert(s.current_direct_lowpass==0 && s.current_room_lowpass==0);
 streams=NULL;mix(out,1024);assert(energy(out,2048)==0);
 puts("PASS: 2D bypass, 3D room/filter send, environment crossfade and live power-off restore dry state");
}
static void benchmark(void){
 float input[1024];for(int i=0;i<1024;i++)input[i]=sinf(i*0.13f)*0.03f;
 reset_room(1);struct timespec a,b;clock_gettime(CLOCK_MONOTONIC,&a);
 for(int block=0;block<1500;block++){memset(out,0,sizeof(out));reverb_process(input,out,1024,1,1);}
 clock_gettime(CLOCK_MONOTONIC,&b);double sec=b.tv_sec-a.tv_sec+(b.tv_nsec-a.tv_nsec)*1e-9;
 printf("BENCH: %.3f ms per 1024-frame (21.33 ms) room block; host CPU only, not Quest performance\n",sec*1000/1500);
}
int main(void){test_dry_identity();test_impulse_toggle();test_parameters();test_routing();benchmark();return 0;}
'''
(OUT / 'reverb.c').write_text(header + body + tests)
for flags, name in [(['-O1', '-fsanitize=address,undefined'], 'reverb-sanitized'), (['-O2'], 'reverb-optimized')]:
    subprocess.run(['clang', '-std=gnu11', *flags, str(OUT / 'reverb.c'), '-lm', '-o', str(OUT / name)], check=True)
    subprocess.run([str(OUT / name)], check=True)
