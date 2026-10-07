/*
VIRTUAL_KEYBOARD.H

header included in hcex build.
*/

#ifndef __VIRTUAL_KEYBOARD_H
#define __VIRTUAL_KEYBOARD_H
#pragma once

/* ---------- headers */

#include "cseries/cseries.h"

/* ---------- constants */

/* ---------- macros */

/* ---------- structures */

/* ---------- prototypes/EXAMPLE.C */

boolean virtual_keyboard_initialize(
	void);
void virtual_keyboard_dispose(
	void);
boolean virtual_keyboard_launch(
	wchar_t *text_buffer,
	word buffer_size,
	short caption_index);
/* Port menu fields: independent of profile/file-name validation. Size is
   bytes, including the terminator; bounded to 128 UTF-16 characters. */
boolean virtual_keyboard_launch_text(
	wchar_t *text_buffer,
	word buffer_size,
	wchar_t const *caption,
	boolean masked);
/* A pointer in the game's 640x480 menu space; selection uses the same keys
   as controller navigation. The caller supplies its already-consumed input. */
void virtual_keyboard_pointer(short x, short y, boolean select, boolean cancel);
boolean virtual_keyboard_active(
	void);
void virtual_keyboard_close(
	void);
boolean virtual_keyboard_last_exit_saved_text(
	void);
void virtual_keyboard_process(
	void);
void virtual_keyboard_render(
	void);

/* ---------- globals */

/* ---------- public code */

#endif // __VIRTUAL_KEYBOARD_H
