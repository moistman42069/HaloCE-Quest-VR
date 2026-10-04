"""Test20: one rigid controller calibration for armed (aim) and empty (grip) hands.

Flat2VR report (2026-10-04): after adjusting the controller alignment, switching
between an empty hand and a held weapon left only one state correct. A held
weapon is oriented by the aim pose and an empty hand by the grip pose; test15
applied the same local angles to each pose separately. These checks execute the
production vr_alignment.h with ASan/UBSan; no headset is used.
Run under Linux/WSL with clang.
"""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/test20-alignment'; OUT.mkdir(parents=True,exist_ok=True)

frame=(ROOT/'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
menu=(ROOT/'port/linux/game/vr_menu.c').read_text(encoding='utf-8')
# Single application point, per physical controller, independent of the weapon hand.
start=frame.index('Once per freshly acquired frame')
block=frame[start:frame.index('update_gestures();',start)]
assert block.count('vr_alignment_apply_controller(')==1 and 'vr_alignment_apply(' not in block
assert 'weapon_hand' not in block and 'alignment_rotation[h]' in block
assert frame.count('vr_alignment_apply')==1, 'calibration must be applied exactly once'
# Menu, reset and reload use the same seven keys per physical side.
for side in ('left','right'):
    for axis in ('pitch','yaw','roll','right','up','back'):
        assert f'"vr.align_{side}_{axis}"' in menu
    assert f'"vr.align_{side}_grip_aim"' in menu
compact=menu.replace(' ','')
assert '{"pitch","yaw","roll","right","up","back"}' in compact
assert 'vr.align_%s_grip_aim' in menu and 'vr.align_%s_%s' in menu and 'vr.align_%s_%s' in frame
assert '"CALIBRATE LEFT"' in menu and '"CALIBRATE RIGHT"' in menu and menu.count('"AIM SOURCE"')==2

c=r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "port/linux/src/vr_alignment.h"
static unsigned seed=12345;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
static void conj(const float q[4],float o[4]){o[0]=-q[0];o[1]=-q[1];o[2]=-q[2];o[3]=q[3];}
static float qdiff(const float a[4],const float b[4]){float d=0,e=0;for(int i=0;i<4;i++){d+=fabsf(a[i]-b[i]);e+=fabsf(a[i]+b[i]);}return d<e?d:e;}
static void relative(const float g[4],const float a[4],float r[4]){float c[4];conj(g,c);vr_alignment_multiply(c,a,r);}
static void random_q(float q[4]){float d[3]={rnd()*360-180,rnd()*360-180,rnd()*360-180};vr_alignment_rotation(d,q);}
int main(void){
 /* Touch-like controller: aim pose tilted from grip about local X plus a tip offset */
 float tilt_deg[3]={-40,0,0},tilt[4];vr_alignment_rotation(tilt_deg,tilt);
 int broke_old=0;
 for(int n=0;n<2000;n++){
  float g[4],a[4],gp[3]={rnd(),1+rnd(),rnd()},ap[3];random_q(g);vr_alignment_multiply(g,tilt,a);
  for(int i=0;i<3;i++)ap[i]=gp[i]+(rnd()-.5f)*.1f;
  float deg[3]={5.f*(int)(rnd()*72-36),5.f*(int)(rnd()*72-36),5.f*(int)(rnd()*72-36)},rot[4];vr_alignment_rotation(deg,rot);
  float off[3]={.01f*(int)(rnd()*40-20),.01f*(int)(rnd()*40-20),.01f*(int)(rnd()*40-20)};
  float G[4],A[4],GP[3],AP[3];memcpy(G,g,16);memcpy(A,a,16);memcpy(GP,gp,12);memcpy(AP,ap,12);
  assert(vr_alignment_apply_controller(GP,G,AP,A,3u,rot,off)==3u);
  /* armed weapon unchanged for saved calibrations: aim orientation and grip
     position are bit-identical to the test15 per-pose path */
  float og[4],oa[4],ogp[3],oap[3];memcpy(og,g,16);memcpy(oa,a,16);memcpy(ogp,gp,12);memcpy(oap,ap,12);
  assert(vr_alignment_apply(ogp,og,rot,off)&&vr_alignment_apply(oap,oa,rot,off));
  assert(!memcmp(A,oa,16)&&!memcmp(GP,ogp,12));
  /* empty hand and weapon stay rigidly related, whatever the correction */
  float before[4],after[4],old[4];relative(g,a,before);relative(G,A,after);relative(og,oa,old);
  assert(qdiff(before,after)<2e-4f);
  if(qdiff(before,old)>1e-2f)broke_old++;
  /* one translation moves both poses */
  for(int i=0;i<3;i++)assert(fabsf((GP[i]-gp[i])-(AP[i]-ap[i]))<1e-5f);
 }
 assert(broke_old>1000);
 /* reported sequence: empty -> pistol -> rifle -> empty, both handedness modes.
    Every frame re-applies to fresh raw poses; nothing accumulates or depends
    on which pose (aim when armed, grip when empty) draws the hand. */
 for(int left_handed=0;left_handed<2;left_handed++){
  float raw_g[2][4],raw_a[2][4],raw_gp[2][3]={{-.2f,1,-.3f},{.2f,1,-.3f}},raw_ap[2][3]={{-.2f,.98f,-.35f},{.2f,.98f,-.35f}};
  float rot[2][4],off[2][3]={{.01f,0,0},{0,-.02f,.03f}},dl[3]={0,15,-20},dr[3]={10,-25,180};
  vr_alignment_rotation(dl,rot[0]);vr_alignment_rotation(dr,rot[1]);
  for(int h=0;h<2;h++){random_q(raw_g[h]);vr_alignment_multiply(raw_g[h],tilt,raw_a[h]);}
  float first[2][2][4];
  for(int f=0;f<4;f++){
   int weapon_hand=left_handed?0:1;
   for(int h=0;h<2;h++){
    float G[4],A[4],GP[3],AP[3];memcpy(G,raw_g[h],16);memcpy(A,raw_a[h],16);memcpy(GP,raw_gp[h],12);memcpy(AP,raw_ap[h],12);
    assert(vr_alignment_apply_controller(GP,G,AP,A,3u,rot[h],off[h])==3u);
    if(!f){memcpy(first[h][0],G,16);memcpy(first[h][1],A,16);}
    assert(!memcmp(first[h][0],G,16)&&!memcmp(first[h][1],A,16));
    int armed=(f==1||f==2)&&h==weapon_hand;const float *drawn=armed?A:G;
    float rel[4],native[4];relative(G,A,rel);relative(raw_g[h],raw_a[h],native);assert(qdiff(rel,native)<2e-4f);
    for(int i=0;i<4;i++)assert(isfinite(drawn[i]));
   }
  }
 }
 /* zero calibration is a byte-preserving no-op */
 {float zero[3]={0},rot[4],g[4],a[4],gp[3]={1,2,3},ap[3]={4,5,6},G[4],A[4],GP[3],AP[3];vr_alignment_rotation(zero,rot);
  random_q(g);vr_alignment_multiply(g,tilt,a);memcpy(G,g,16);memcpy(A,a,16);memcpy(GP,gp,12);memcpy(AP,ap,12);
  assert(vr_alignment_apply_controller(GP,G,AP,A,3u,rot,zero)==3u);
  assert(!memcmp(G,g,16)&&!memcmp(A,a,16)&&!memcmp(GP,gp,12)&&!memcmp(AP,ap,12));}
 /* AIM SOURCE = GRIP copies grip into aim first: identical to test15 */
 {float d[3]={20,-35,90},rot[4],off[3]={.05f,0,-.1f},g[4],gp[3]={0,1,0},G[4],A[4],GP[3],AP[3],og[4],ogp[3];
  vr_alignment_rotation(d,rot);random_q(g);
  memcpy(G,g,16);memcpy(A,g,16);memcpy(GP,gp,12);memcpy(AP,gp,12);memcpy(og,g,16);memcpy(ogp,gp,12);
  assert(vr_alignment_apply_controller(GP,G,AP,A,3u,rot,off)==3u);assert(vr_alignment_apply(ogp,og,rot,off));
  assert(!memcmp(A,og,16)&&qdiff(G,og)<1e-5f&&!memcmp(GP,ogp,12));}
 /* invalid/missing poses: the other pose is corrected alone, exactly as before */
 {float d[3]={0,30,0},rot[4],off[3]={.02f,0,0},g[4],a[4],gp[3]={0,1,0},ap[3]={0,1,-.05f};
  vr_alignment_rotation(d,rot);random_q(g);vr_alignment_multiply(g,tilt,a);
  float G[4],A[4],GP[3],AP[3],oa[4],oap[3],og[4],ogp[3];
  memcpy(G,g,16);memcpy(A,a,16);memcpy(GP,gp,12);memcpy(AP,ap,12);memcpy(oa,a,16);memcpy(oap,ap,12);
  G[0]=NAN;assert(vr_alignment_apply_controller(GP,G,AP,A,3u,rot,off)==2u);
  assert(vr_alignment_apply(oap,oa,rot,off));assert(!memcmp(A,oa,16)&&!memcmp(AP,oap,12));
  memcpy(G,g,16);memcpy(GP,gp,12);memcpy(og,g,16);memcpy(ogp,gp,12);memcpy(A,a,16);
  assert(vr_alignment_apply_controller(GP,G,AP,A,1u,rot,off)==1u);
  assert(vr_alignment_apply(ogp,og,rot,off));assert(!memcmp(G,og,16)&&!memcmp(GP,ogp,12));
  memset(A,0,16);memcpy(G,g,16);assert(vr_alignment_apply_controller(GP,G,AP,A,3u,rot,off)==1u);
  GP[1]=INFINITY;assert(vr_alignment_apply_controller(GP,G,AP,A,1u,rot,off)==0u);}
 printf("PASS: 2000 random calibrations keep empty hand and weapon rigid (test15 path broke %d); weapon pose bit-identical for saved settings\n",broke_old);
 puts("PASS: empty -> pistol -> rifle -> empty, both handedness modes, no accumulation; zero no-op; AIM SOURCE grip; invalid-pose fallbacks");
}
'''
(OUT/'alignment.c').write_text(c)
subprocess.run(['clang','-std=c11','-O1','-Wall','-Wextra','-Wno-unused-function','-fsanitize=address,undefined','-I',str(ROOT),
                str(OUT/'alignment.c'),'-lm','-o',str(OUT/'alignment')],check=True)
subprocess.run([str(OUT/'alignment')],check=True)
