/* the game includes <StdDef.h>; Linux file names are case sensitive. On a
case-insensitive file system (macOS) <stddef.h> would find this file again,
so the real one is searched for past this directory. */
#include_next <stddef.h>
