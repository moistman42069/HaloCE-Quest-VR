/* Controller-local calibration shared by grip, aim, IK, contacts and avatars.
 * Rotation order: local yaw(Y), pitch(X), roll(Z); position is in the ORIGINAL
 * controller frame (+X right, +Y up, +Z back), metres. No reflected matrices.
 * Zero correction is a byte-preserving no-op for accepted controller poses. */
#ifndef HALO_VR_ALIGNMENT_H
#define HALO_VR_ALIGNMENT_H
#include <math.h>
#include <string.h>
static float vr_alignment_bound(double value, float limit)
{
    return isfinite(value) ? (float)fmax(-limit, fmin(limit, value)) : 0.f;
}
static void vr_alignment_multiply(const float a[4], const float b[4], float out[4])
{
    float t[4] = {
        a[3]*b[0]+a[0]*b[3]+a[1]*b[2]-a[2]*b[1],
        a[3]*b[1]-a[0]*b[2]+a[1]*b[3]+a[2]*b[0],
        a[3]*b[2]+a[0]*b[1]-a[1]*b[0]+a[2]*b[3],
        a[3]*b[3]-a[0]*b[0]-a[1]*b[1]-a[2]*b[2] };
    memcpy(out,t,sizeof(t));
}
static void vr_alignment_rotation(const float degrees[3], float out[4])
{
    const float radians = 0.00872664626f;
    float p=degrees[0]*radians,y=degrees[1]*radians,r=degrees[2]*radians;
    float pitch[4]={sinf(p),0,0,cosf(p)},yaw[4]={0,sinf(y),0,cosf(y)},roll[4]={0,0,sinf(r),cosf(r)};
    vr_alignment_multiply(yaw,pitch,out); vr_alignment_multiply(out,roll,out);
}
static int vr_alignment_apply(float position[3], float orientation[4], const float rotation[4], const float offset[3])
{
    float q[4], translated[3], n=0.f; int i;
    for(i=0;i<4;i++) { if(!isfinite(orientation[i])) return 0; n+=orientation[i]*orientation[i]; }
    for(i=0;i<3;i++) if(!isfinite(position[i])) return 0;
    if(n<0.25f || n>4.f) return 0;
    if(rotation[0]==0.f && rotation[1]==0.f && rotation[2]==0.f && rotation[3]==1.f &&
        offset[0]==0.f && offset[1]==0.f && offset[2]==0.f) return 1;
    n=sqrtf(n); for(i=0;i<4;i++) q[i]=orientation[i]/n;
    /* q * (offset,0) * conjugate(q). */
    {
        float v[4]={offset[0],offset[1],offset[2],0}, inverse[4]={-q[0],-q[1],-q[2],q[3]}, t[4];
        vr_alignment_multiply(q,v,t); vr_alignment_multiply(t,inverse,t);
        for(i=0;i<3;i++) translated[i]=position[i]+t[i];
    }
    vr_alignment_multiply(q,rotation,orientation);
    memcpy(position,translated,sizeof(translated)); return 1;
}
#endif
