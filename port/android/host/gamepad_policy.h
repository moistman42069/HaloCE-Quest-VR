#ifndef HALO_ANDROID_GAMEPAD_POLICY_H
#define HALO_ANDROID_GAMEPAD_POLICY_H
#include <math.h>

/* Encode the requested post-dead-zone value for the guest's existing 9000
 * axial dead zone (source/input/input_xbox.c). Do not apply two dead zones.
 * This transform is used only for physical pads in the flat Android host. */
static inline int halo_pad_axis(int raw, float dead, float gain, int invert)
{
    if (!isfinite(dead) || dead < 0 || dead > .45f) dead = 9000.f / 32767.f;
    if (!isfinite(gain) || gain < .25f || gain > 2.f) gain = 1.f;
    float value = raw / 32767.f;
    if (invert) value = -value;
    float amount = (fabsf(value) - dead) / (1.f - dead);
    if (amount <= 0) return 0;
    amount = fminf(1.f, amount * gain);
    return (int)copysignf(9000.f + amount * (32767.f - 9000.f), value);
}

static inline int halo_pad_trigger(int raw, float dead)
{
    if (!isfinite(dead) || dead < 0 || dead > .4f) dead = .05f;
    float amount = (raw / 32767.f - dead) / (1.f - dead);
    return (int)(fmaxf(0, fminf(1, amount)) * 32767.f);
}
#endif
