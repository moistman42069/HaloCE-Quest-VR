"""Production music/effects/master-volume consumers, without an audio device."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test31-audio'
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return (ROOT / path).read_text()


def fn(text, name):
    match = re.search(r'^(?:static )?[\w *]+\b' + re.escape(name) +
                      r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert match, name
    start = text.index('{', match.start())
    end, depth = start + 1, 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[match.start():end] + '\n'


sound = read('source/sound/sound_manager.c')
mixer = read('port/linux/src/dsound_sdl.c')
config = read('port/linux/src/port_config.c')
for setting in ('audio.volume', 'audio.music_volume', 'audio.effects_volume'):
    assert re.search(r'\{ "' + re.escape(setting) + r'", _config_real, "1\.0"', config), setting
assert 'audio_update_volume();' in fn(mixer, 'audio_start')
work = fn(mixer, 'DirectSoundDoWork')
assert 'audio_update_volume();' in work and 'audio_statistics_log();' in work
assert 'audio_update_volume' not in fn(mixer, 'mix')
assert 'config_' not in fn(mixer, 'audio_callback')

source = r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
typedef float real;
#define PIN(x,lo,hi) ((x)<(lo)?(lo):((x)>(hi)?(hi):(x)))
enum { _sound_class_music=26, _sound_class_scripted_dialog_to_player=20,
 _sound_class_scripted_dialog_to_other=21, _sound_class_scripted_dialog_force_unspatialized=22 };
static struct {real nondialog_gain;} sound_manager_globals;
static unsigned long generation;
static float music=1, effects=1, master=1, scripted_gain=1, master_volume=1;
static int reads, locked, locks, unlocks, mixer_lock;
unsigned long config_changes(void){return generation;}
double config_real(const char *key){
 assert(!locked);reads++;
 if(!strcmp(key,"audio.music_volume"))return music;
 if(!strcmp(key,"audio.effects_volume"))return effects;
 assert(!strcmp(key,"audio.volume"));return master;
}
static real sound_class_get_gain(short c){return scripted_gain;}
static void pthread_mutex_lock(int *lock){assert(lock==&mixer_lock && !locked);locked=1;locks++;}
static void pthread_mutex_unlock(int *lock){assert(lock==&mixer_lock && locked);locked=0;unlocks++;}
''' + fn(sound, 'sound_manager_port_volume') + fn(sound, 'sound_manager_master_gain') + \
    fn(mixer, 'audio_update_volume') + r'''
static int dialog(int c){return c==20 || c==21 || c==22;}
static void close_enough(float a,float b){assert(fabsf(a-b)<0.00001f);}
int main(void){
 sound_manager_globals.nondialog_gain=0.5f;scripted_gain=0.4f;
 for(int c=0;c<35;c++)close_enough(sound_manager_master_gain(c),dialog(c)?0.4f:0.2f);
 assert(reads==2); /* defaults preserve every class and script fade */
 music=0.3f;effects=0.7f;generation++;
 for(int c=0;c<35;c++)close_enough(sound_manager_master_gain(c),
     (dialog(c)?0.4f:0.2f)*(c==26?0.3f:0.7f));
 assert(reads==4);
 music=0;effects=0; /* no config change: cached values stay in effect */
 close_enough(sound_manager_port_volume(26),0.3f);assert(reads==4);
 generation++;assert(sound_manager_master_gain(26)==0 && sound_manager_master_gain(20)==0);
 music=2;effects=-2;generation++;
 assert(sound_manager_port_volume(26)==1 && sound_manager_port_volume(2)==0);
 music=NAN;effects=INFINITY;generation++;
 assert(sound_manager_port_volume(26)==1 && sound_manager_port_volume(2)==1);
 audio_update_volume();assert(master_volume==1 && locks==1 && unlocks==1);
 int old_reads=reads;audio_update_volume();assert(reads==old_reads && locks==1);
 master=0.25f;generation++;audio_update_volume();assert(master_volume==0.25f);
 master=0;generation++;audio_update_volume();assert(master_volume==0);
 master=2;generation++;audio_update_volume();assert(master_volume==2); /* preserve legacy gain boost */
 master=-1;generation++;audio_update_volume();assert(master_volume==0);
 master=NAN;generation++;audio_update_volume();assert(master_volume==1);
 assert(locks==unlocks && !locked);
 puts("PASS: production volume defaults, music/effects separation, script/dialog gain, cached live updates, finite bounds, master mutex and legacy boost");
}
'''
(OUT / 'audio.c').write_text(source)
subprocess.run(['clang', '-std=gnu11', '-O1', '-fsanitize=address,undefined',
                str(OUT / 'audio.c'), '-lm', '-o', str(OUT / 'audio')], check=True)
subprocess.run([str(OUT / 'audio')], check=True)
print('PASS: startup/live master wiring preserves diagnostics; no config reads in mixer callback')
