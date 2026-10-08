"""Full production config: APK Safe defaults/migration, opt-out and I/O faults.

SDL file/path boundaries are fixtures only for the desktop compatibility check.
Android compiles the actual stdio persistence and atomic migration functions.
"""
from pathlib import Path
import os
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/test32-geometry'
OUT.mkdir(parents=True,exist_ok=True)
production=(ROOT/'port/linux/src/port_config.c').read_text().replace('#include "platform.h"','static void platform_log(const char *s,...) {(void)s;}').replace(
 '#include "halo_port_limits.h"','#define HALO_PORT_NETWORK_VERSION 24\n#define HALO_PORT_NETWORK_VERSION_MINIMUM 11\n#define HALO_PORT_NETWORK_VERSION_MAXIMUM 24').replace('#include <SDL3/SDL.h>','')
boundaries=r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
static FILE *fault_file;
static FILE *fault_fopen(const char *path,const char *mode){
 const char *fault=getenv("TEST_GEOMETRY_FAULT");
 if(fault&&!strcmp(fault,"backup-unreadable")&&strchr(mode,'r')&&strstr(path,".pre-safe-geometry")){errno=EACCES;return NULL;}
 if(fault&&strchr(mode,'w')&&(!strcmp(fault,"readonly")||
   (!strcmp(fault,"backup")&&strstr(path,".pre-safe-geometry"))||
   (!strcmp(fault,"temporary")&&strstr(path,".safe-geometry.tmp")))){errno=EACCES;return NULL;}
 FILE *file=fopen(path,mode);
 if(fault&&strchr(mode,'w')&&
   (((!strcmp(fault,"backup-short")||!strcmp(fault,"backup-close"))&&strstr(path,".pre-safe-geometry"))||
    ((!strcmp(fault,"temporary-short")||!strcmp(fault,"temporary-close"))&&strstr(path,".safe-geometry.tmp"))))fault_file=file;
 return file;
}
static size_t fault_fwrite(const void *data,size_t size,size_t count,FILE *file){
 const char *fault=getenv("TEST_GEOMETRY_FAULT");
 if(file==fault_file&&fault&&strstr(fault,"-short")){fwrite(data,size,count/2,file);errno=ENOSPC;return count/2;}
 return fwrite(data,size,count,file);
}
static int fault_fclose(FILE *file){
 const char *fault=getenv("TEST_GEOMETRY_FAULT");int selected=file==fault_file;int result=fclose(file);
 if(selected){fault_file=NULL;if(fault&&strstr(fault,"-close")){errno=ENOSPC;return EOF;}}return result;
}
static int fault_rename(const char *a,const char *b){
 const char *fault=getenv("TEST_GEOMETRY_FAULT");
 if(fault&&!strcmp(fault,"rename")){errno=EACCES;return -1;}return rename(a,b);
}
#define fopen fault_fopen
#define fwrite fault_fwrite
#define fclose fault_fclose
#define rename fault_rename
#ifndef HALO_ANDROID
static const char *SDL_GetBasePath(void){return getenv("TEST_CONFIG_BASE");}
static void *SDL_LoadFile(const char *path,size_t *size){
 FILE *f=fopen(path,"rb");char *p;long n;if(!f)return NULL;
 fseek(f,0,SEEK_END);n=ftell(f);rewind(f);p=malloc(n+1);
 if(!p||fread(p,1,n,f)!=(size_t)n){free(p);p=NULL;}else{p[n]=0;*size=n;}fclose(f);return p;
}
static int SDL_SaveFile(const char *path,const void *data,size_t size){
 FILE *f=fopen(path,"wb");int ok;if(!f)return 0;ok=fwrite(data,1,size,f)==size;return fclose(f)==0&&ok;
}
#define SDL_free free
#endif
'''
main=r'''
#include <assert.h>
int main(int argc,char **argv){
 char value[16];assert(argc>=3);
 assert(config_default("renderer.safe_geometry",value,sizeof(value)));
 assert(!strcmp(value,atoi(argv[2])?"true":"false"));
 assert(config_boolean("renderer.safe_geometry")==atoi(argv[1]));
 if(argc>3){assert(config_write_boolean("renderer.safe_geometry",atoi(argv[3])));assert(config_boolean("renderer.safe_geometry")==atoi(argv[3]));}
 return 0;
}
'''

def environment(folder,**overrides):
    env=dict(os.environ,HALO_DATA_ROOT=str(folder),TEST_CONFIG_BASE=str(folder)+'/')
    for key in ('HALO_SAFE_GEOMETRY','HALO_VR_GEOMETRY_REVISION','HALO_ANDROID_GEOMETRY_REVISION','TEST_GEOMETRY_FAULT'):
        env.pop(key,None)
    env.update(overrides)
    return env


def run(exe,folder,expected,default=1,write=None,**overrides):
    args=[str(exe),str(int(expected)),str(default)]
    if write is not None:args.append(str(int(write)))
    subprocess.run(args,env=environment(folder,**overrides),check=True)


for edition,defines in (('flat','#define HALO_ANDROID 1\n'),('vr','#define HALO_ANDROID 1\n#define HALO_VR 1\n'),('desktop','')):
    c=OUT/(edition+'.c');exe=OUT/edition
    c.write_text(defines+boundaries+production+main)
    subprocess.run(['clang','-std=gnu11','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',
                    '-I'+str(ROOT/'port/linux/src'),'-I'+str(ROOT/'port/third_party/tomlc17'),str(c),
                    str(ROOT/'port/third_party/tomlc17/tomlc17.c'),'-pthread','-lm','-o',str(exe)],check=True)
    revision='vr_geometry_revision' if edition=='vr' else 'android_geometry_revision'
    if edition=='desktop':
        for initial,expected in ((None,False),('[renderer]\nsafe_geometry=false\n',False),('[renderer]\nsafe_geometry=true\n',True)):
            with tempfile.TemporaryDirectory(dir=OUT) as folder:
                path=Path(folder)/'config.toml'
                if initial:path.write_text(initial)
                run(exe,folder,expected,0)
                assert not (Path(folder)/'config.toml.pre-safe-geometry').exists()
                assert not re.search(r'^\s*(?:vr|android)_geometry_revision\s*=',path.read_text(),re.M)
                run(exe,folder,not expected,0,HALO_SAFE_GEOMETRY='false' if expected else 'true')
        print('PASS desktop: unchanged Normal default, stored Safe/Normal and environment precedence',flush=True)
        continue
    for rev in ('1','2','999'):
        with tempfile.TemporaryDirectory(dir=OUT) as folder:
            path=Path(folder)/'config.toml'
            path.write_text(f'[renderer]\nsafe_geometry=false\n{revision}={rev}\n')
            run(exe,folder,False);run(exe,folder,False)
            run(exe,folder,True,HALO_SAFE_GEOMETRY='true');run(exe,folder,False)
            assert not (Path(folder)/'config.toml.pre-safe-geometry').exists()
    for rev in ('0','-1','"1"','false'):
        with tempfile.TemporaryDirectory(dir=OUT) as folder:
            path=Path(folder)/'config.toml'
            initial=f'# keep\n[renderer]\nsafe_geometry=false\n{revision}={rev}\n[network]\nonline=false\n'.encode()
            path.write_bytes(initial);run(exe,folder,True)
            assert (Path(folder)/'config.toml.pre-safe-geometry').read_bytes()==initial
            assert re.search(revision+r'\s*=\s*1\b',path.read_text())
            run(exe,folder,True,write=False);run(exe,folder,False)
            run(exe,folder,False,write=True);run(exe,folder,True)
            assert (Path(folder)/'config.toml.pre-safe-geometry').read_bytes()==initial
    for failure in ('readonly','backup','temporary','rename','backup-short','backup-close','temporary-short','temporary-close'):
        with tempfile.TemporaryDirectory(dir=OUT) as folder:
            path=Path(folder)/'config.toml'
            original=b'# untouched\r\n[renderer]\r\nsafe_geometry=false\r\n[network]\r\nonline=false\r\n'
            path.write_bytes(original)
            for attempt in range(2):
                run(exe,folder,True,TEST_GEOMETRY_FAULT=failure)
                assert path.read_bytes()==original
                assert not (Path(folder)/'config.toml.safe-geometry.tmp').exists()
                backup=Path(folder)/'config.toml.pre-safe-geometry'
                assert not backup.exists() or backup.read_bytes()==original
            # Successful retry preserves exact original backup and applies Safe.
            run(exe,folder,True);run(exe,folder,True)
            assert (Path(folder)/'config.toml.pre-safe-geometry').read_bytes()==original
    for malformed in ('[renderer]\nsafe_geometry=nope\n','renderer={safe_geometry=false}\n','renderer.safe_geometry=false\n'):
        with tempfile.TemporaryDirectory(dir=OUT) as folder:
            path=Path(folder)/'config.toml';path.write_text(malformed)
            run(exe,folder,True);run(exe,folder,True)
            assert path.read_text()==malformed
    with tempfile.TemporaryDirectory(dir=OUT) as folder:
        path=Path(folder)/'config.toml';original=b'[renderer]\nsafe_geometry=false\n';path.write_bytes(original)
        backup=Path(folder)/'config.toml.pre-safe-geometry';backup.write_bytes(b'# older preserved backup\n')
        run(exe,folder,True,TEST_GEOMETRY_FAULT='backup-unreadable')
        assert path.read_bytes()==original and backup.read_bytes()==b'# older preserved backup\n'
        run(exe,folder,True)
        assert backup.read_bytes()==b'# older preserved backup\n'
    # Environment overrides runtime after migration; it does not persist an
    # opt-out or incorrectly skip the edition's disk migration.
    with tempfile.TemporaryDirectory(dir=OUT) as folder:
        path=Path(folder)/'config.toml';path.write_text('[renderer]\nsafe_geometry=false\n')
        run(exe,folder,False,HALO_SAFE_GEOMETRY='false',HALO_VR_GEOMETRY_REVISION='99',HALO_ANDROID_GEOMETRY_REVISION='99')
        assert re.search(r'^safe_geometry\s*=\s*true',path.read_text(),re.M)
        assert re.search(revision+r'\s*=\s*1\b',path.read_text())
        run(exe,folder,True)
    # The other edition's marker cannot bypass this edition's first migration.
    with tempfile.TemporaryDirectory(dir=OUT) as folder:
        other='android_geometry_revision' if edition=='vr' else 'vr_geometry_revision'
        (Path(folder)/'config.toml').write_text(f'[renderer]\nsafe_geometry=false\n{other}=1\n')
        run(exe,folder,True)
    print('PASS '+edition+': migration revisions/atomic failures/retry/backup/opt-out/custom syntax/environment',flush=True)
