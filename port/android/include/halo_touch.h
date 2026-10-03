/* Flat Android touch input. Fixed-width snapshot across the host/guest ABI.
 * Button bit order is shared with TouchControls.java; axes use Xbox signs
 * (positive Y is up) and the range [-32767, 32767]. No controller is added. */
#ifndef HALO_TOUCH_H
#define HALO_TOUCH_H

struct halo_touch_state
{
	int lx, ly, rx, ry;
	unsigned int buttons;
	float yaw, pitch; /* accumulated relative radians; consumed once per poll */
	unsigned int generation; /* cancellation clears already-polled motion */
};

#define HALO_TOUCH_A        (1u << 0)
#define HALO_TOUCH_B        (1u << 1)
#define HALO_TOUCH_X        (1u << 2)
#define HALO_TOUCH_Y        (1u << 3)
#define HALO_TOUCH_WHITE    (1u << 4)
#define HALO_TOUCH_BLACK    (1u << 5)
#define HALO_TOUCH_CROUCH   (1u << 6)
#define HALO_TOUCH_ZOOM     (1u << 7)
#define HALO_TOUCH_START    (1u << 8)
#define HALO_TOUCH_BACK     (1u << 9)
#define HALO_TOUCH_UP       (1u << 10)
#define HALO_TOUCH_DOWN     (1u << 11)
#define HALO_TOUCH_LEFT     (1u << 12)
#define HALO_TOUCH_RIGHT    (1u << 13)
#define HALO_TOUCH_GRENADE  (1u << 14)
#define HALO_TOUCH_FIRE     (1u << 15)

#endif
