#!/usr/bin/env python3
"""Copy the maps folder out of a Halo Xbox disc image (.iso or .xiso).

The same reading of XDVDFS as port/linux/src/xiso.c (after extract-xiso):
2048-byte sectors, a volume descriptor at 0x10000 inside the game partition
("MICROSOFT*XBOX*MEDIA" at both ends, then the root directory's sector and
size), and directories whose entries form a binary tree of
(left, right, sector, size, attributes, name length, name). Whole-disc
images put the game partition at one of the offsets below.

Usage: extract_maps.py image.iso destination   (writes destination/maps)
"""

import os
import struct
import sys

SECTOR = 2048
DESCRIPTOR = 0x10000
MAGIC = b"MICROSOFT*XBOX*MEDIA"
PARTITIONS = (0, 0x0FD90000, 0x02080000, 0x18300000)
DIRECTORY_BIT = 0x10


def find_partition(image):
    for partition in PARTITIONS:
        image.seek(partition + DESCRIPTOR)
        block = image.read(SECTOR)
        if block[:20] == MAGIC and block[0x7EC:0x800] == MAGIC:
            root_sector, root_size = struct.unpack_from("<II", block, 20)
            return partition, root_sector, root_size
    raise SystemExit("not an Xbox disc image (no XDVDFS volume descriptor)")


def entries(image, partition, sector, size):
    image.seek(partition + sector * SECTOR)
    table = image.read(size)
    found, pending, seen = [], [0], set()
    while pending:
        offset = pending.pop() * 4
        if offset in seen or offset + 14 > len(table):
            continue
        seen.add(offset)
        left, right, start, length, attributes, name_length = struct.unpack_from("<HHIIBB", table, offset)
        if left == 0xFFFF:  # padding to the end of the sector
            continue
        name = table[offset + 14:offset + 14 + name_length].decode("latin-1")
        found.append((name, start, length, attributes))
        for child in (left, right):
            if child:
                pending.append(child)
    return found


def copy_tree(image, partition, sector, size, destination):
    os.makedirs(destination, exist_ok=True)
    for name, start, length, attributes in entries(image, partition, sector, size):
        target = os.path.join(destination, name)
        if attributes & DIRECTORY_BIT:
            if length:
                copy_tree(image, partition, start, length, target)
            else:
                os.makedirs(target, exist_ok=True)
            continue
        image.seek(partition + start * SECTOR)
        remaining = length
        with open(target, "wb") as out:
            while remaining:
                chunk = image.read(min(remaining, 1 << 20))
                if not chunk:
                    raise SystemExit(f"{name}: the image ends early")
                out.write(chunk)
                remaining -= len(chunk)
        print(f"  {name} ({length // 1024} KB)")


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    image_path, destination = sys.argv[1], sys.argv[2]
    with open(image_path, "rb") as image:
        partition, root_sector, root_size = find_partition(image)
        for name, start, length, attributes in entries(image, partition, root_sector, root_size):
            if name.lower() == "maps" and attributes & DIRECTORY_BIT:
                partial = os.path.join(destination, "maps.partial")
                copy_tree(image, partition, start, length, partial)
                final = os.path.join(destination, "maps")
                if os.path.exists(final):
                    raise SystemExit(f"{final} exists; remove it first")
                os.rename(partial, final)
                print(f"maps extracted to {final}")
                return
    raise SystemExit("no maps folder at the image's root")


if __name__ == "__main__":
    main()
