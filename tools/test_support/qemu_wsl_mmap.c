/* Test-process-only WSL1 compatibility for QEMU's reservation probe.
 * WSL1 rejects MAP_FIXED_NOREPLACE. A normal mmap hint is safe: it cannot
 * replace an existing mapping. Accept it only if the exact address was free.
 * This is never linked into Halo, an APK, or any installed application. */
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/mman.h>
#include <dlfcn.h>
#include <errno.h>

typedef void *(*mmap_function)(void *, size_t, int, int, int, off64_t);

static void *mmap_noreplace_compat(mmap_function real_mmap, void *address,
    size_t length, int protection, int flags, int descriptor, off64_t offset)
{
    void *result = real_mmap(address, length, protection, flags, descriptor, offset);
    if (result == MAP_FAILED && (errno == EINVAL || errno == EOPNOTSUPP) &&
        address && (flags & MAP_FIXED_NOREPLACE) && !(flags & MAP_FIXED))
    {
        /* Removing NOREPLACE deliberately does not add MAP_FIXED. */
        result = real_mmap(address, length, protection, flags & ~MAP_FIXED_NOREPLACE,
            descriptor, offset);
        if (result != MAP_FAILED && result != address)
        {
            munmap(result, length);
            errno = EEXIST;
            return MAP_FAILED;
        }
    }
    return result;
}

void *mmap64(void *address, size_t length, int protection, int flags,
    int descriptor, off64_t offset)
{
    static mmap_function real_mmap;
    if (!real_mmap)
        real_mmap = (mmap_function)dlsym(RTLD_NEXT, "mmap64");
    if (!real_mmap)
    {
        errno = ENOSYS;
        return MAP_FAILED;
    }
    return mmap_noreplace_compat(real_mmap, address, length, protection, flags,
        descriptor, offset);
}
