package com.halo.decomp;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * Copies the maps folder out of an Xbox disc image (an "xiso", or a whole
 * disc's ".iso"), as the desktop games do (port/linux/src/xiso.c, which this
 * follows).
 *
 * The image's file system is XDVDFS, read as extract-xiso does
 * (https://github.com/XboxDev/extract-xiso, extract-xiso.c, whose format
 * handling this follows; its license is below and in
 * port/third_party/extract-xiso/LICENSE.TXT): 2048-byte sectors; a volume
 * descriptor at 0x10000 that starts and ends with "MICROSOFT*XBOX*MEDIA" and
 * gives the root directory's sector and size; and directories whose entries
 * form a binary tree (each entry: left and right subtree offsets in 4-byte
 * units, the start sector, the size, attributes, the name's length and the
 * name, 4-byte aligned). Images made from a whole disc put the game partition
 * further in, at one of the offsets below.
 *
 * The files are written to maps.partial first and moved into maps once they
 * all are, so an interrupted extraction never leaves maps/ui.map behind.
 *
 * Some parts of this code are copyright in@fishtank.com. This product
 * includes software developed by in &lt;in@fishtank.com&gt;.
 *
 * Copyright (c) 2003 in &lt;in@fishtank.com&gt;
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * 3. All advertising materials mentioning features or use of this software
 *    must display the following acknowledgement:
 *
 *    This product includes software developed by in &lt;in@fishtank.com&gt;.
 *
 * 4. Neither the name of "in" nor the email address "in@fishtank.com"
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED `AS IS' AND ANY EXPRESS OR IMPLIED WARRANTIES
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
 * AUTHOR OR ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
final class XisoExtractor {
    private static final int SECTOR_SIZE = 2048;
    private static final long VOLUME_DESCRIPTOR_OFFSET = 0x10000;
    private static final int ENTRY_HEADER_SIZE = 14;
    private static final int ATTRIBUTE_DIRECTORY = 0x10;
    /* directory tables are a few sectors; anything much larger is not one */
    private static final long MAXIMUM_DIRECTORY_SIZE = 4 << 20;
    private static final int MAXIMUM_FILES = 4096;
    private static final int COPY_BUFFER_SIZE = 1 << 20;
    private static final byte[] VOLUME_MAGIC = "MICROSOFT*XBOX*MEDIA".getBytes(StandardCharsets.US_ASCII);

    /* where the game partition starts: a plain image, and whole-disc images
    (extract-xiso's GLOBAL, XGD3 and XGD1 offsets) */
    private static final long[] PARTITION_OFFSETS = { 0, 0x0FD90000L, 0x02080000L, 0x18300000L };

    interface Progress {
        void report(String file, long done, long total);
    }

    /** a reason the player can act on */
    static final class ExtractException extends IOException {
        ExtractException(String message) {
            super(message);
        }
    }

    private static final class Entry {
        final String name;
        final long sector;
        final long size;

        Entry(String name, long sector, long size) {
            this.name = name.toLowerCase(java.util.Locale.ROOT);
            this.sector = sector;
            this.size = size;
        }
    }

    private final FileChannel image;
    private long partition;

    private XisoExtractor(FileChannel image) {
        this.image = image;
    }

    /** copies the image's maps folder to destination/maps */
    static void extractMaps(FileChannel image, File destination, Progress progress) throws IOException {
        new XisoExtractor(image).extract(destination, progress);
    }

    private void readAt(long offset, ByteBuffer buffer) throws IOException {
        while (buffer.hasRemaining()) {
            if(Thread.currentThread().isInterrupted())throw new java.io.InterruptedIOException("Import cancelled");
            int count;
            try { count = image.read(buffer, offset); }
            catch (java.nio.channels.ClosedByInterruptException e) { throw new java.io.InterruptedIOException("Import cancelled"); }
            catch (IOException e) { throw new ExtractException("Cannot seek/read the image. Copy the complete ISO/XISO to this device's Downloads folder, then select that local copy. " + e.getMessage()); }

            if (count <= 0)
                throw new ExtractException("Could not read the disc image (is it complete?).");
            offset += count;
        }
        buffer.flip();
    }

    private static boolean magicAt(ByteBuffer buffer, int offset) {
        for (int index = 0; index < VOLUME_MAGIC.length; index++) {
            if (buffer.get(offset + index) != VOLUME_MAGIC[index])
                return false;
        }
        return true;
    }

    /** the partition's volume descriptor: the root directory's sector and size */
    private long[] findVolume() throws IOException {
        if (Thread.currentThread().isInterrupted()) throw new java.io.InterruptedIOException("Import cancelled");
        long size = image.size();
        if (size < VOLUME_DESCRIPTOR_OFFSET + SECTOR_SIZE)
            throw new ExtractException("Image is too short (" + size + " bytes). Finish transferring the complete ISO/XISO to local Downloads first.");
        boolean damaged = false;
        for (long offset : PARTITION_OFFSETS) {
            if (offset + VOLUME_DESCRIPTOR_OFFSET + SECTOR_SIZE > size) continue;
            ByteBuffer descriptor = ByteBuffer.allocate(SECTOR_SIZE).order(ByteOrder.LITTLE_ENDIAN);
            readAt(offset + VOLUME_DESCRIPTOR_OFFSET, descriptor);
            boolean first = magicAt(descriptor, 0), last = magicAt(descriptor, 0x7EC);
            damaged |= first != last;
            if (!first || !last)
                continue;
            partition = offset;
            return new long[] {
                descriptor.getInt(20) & 0xFFFFFFFFL, descriptor.getInt(24) & 0xFFFFFFFFL,
            };
        }
        throw new ExtractException(damaged ?
            "The Xbox volume header is damaged. Compare the file size/checksum with the source and copy the complete image again." :
            "No Xbox game partition found in " + size + " bytes. Use a complete original-Xbox Halo CE ISO/XISO, or import its extracted maps folder. Unpack ZIP/7z/RAR archives and merge split image parts first. PC/MCC disc images are different formats. If this file works on another device, compare file sizes/checksums and copy it again to local Downloads.");
    }

    /** a directory's table, read whole */
    private ByteBuffer readDirectory(long sector, long size, String what) throws IOException {
        if (size <= 0 || size > MAXIMUM_DIRECTORY_SIZE)
            throw new ExtractException(what);
        if (partition + sector * SECTOR_SIZE > image.size() - size)
            throw new ExtractException("Truncated disc image: directory extends past the file. Complete the transfer before importing.");
        ByteBuffer table = ByteBuffer.allocate((int) size).order(ByteOrder.LITTLE_ENDIAN);
        readAt(partition + sector * SECTOR_SIZE, table);
        return table;
    }

    /**
     * collects the entries of the subtree at offset (4-byte units), files or
     * directories as asked
     */
    private static void walk(ByteBuffer table, boolean directories, List<Entry> out) throws IOException {
        /* Valid repacked images can have a very deep, unbalanced tree (also
         * documented by extract-xiso). Do not silently truncate it at depth 64.
         * Offsets are uint16 units of four bytes; an explicit stack plus visited
         * set bounds work without consuming the Java call stack. */
        java.util.ArrayDeque<Integer> pending = new java.util.ArrayDeque<>();
        java.util.BitSet visited = new java.util.BitSet(65536);
        pending.push(0);
        while (!pending.isEmpty()) {
            if (Thread.currentThread().isInterrupted()) throw new java.io.InterruptedIOException("Import cancelled");
            int offset = pending.pop(), at = offset * 4;
            if (visited.get(offset) || at + ENTRY_HEADER_SIZE > table.limit())
                throw new ExtractException("Damaged Xbox directory tree (repeated or out-of-range entry).");
            visited.set(offset);
            int left = table.getShort(at) & 0xFFFF;
            int right = table.getShort(at + 2) & 0xFFFF;
            if (left == 0xFFFF) continue; // empty table/padding
            int nameLength = table.get(at + 13) & 0xFF;
            if (nameLength == 0 || at + ENTRY_HEADER_SIZE + nameLength > table.limit())
                throw new ExtractException("Damaged Xbox directory filename.");
            byte[] bytes = new byte[nameLength];
            for (int index = 0; index < nameLength; index++)
                bytes[index] = table.get(at + ENTRY_HEADER_SIZE + index);
            String name = new String(bytes, StandardCharsets.ISO_8859_1);
            /* (as extract-xiso refuses them: no name may leave the folder) */
            if (name.equals(".") || name.equals("..") || name.indexOf('/') >= 0 || name.indexOf('\\') >= 0 || name.indexOf('\0') >= 0)
                throw new ExtractException("Unsafe filename in Xbox directory.");
            boolean isDirectory = (table.get(at + 12) & ATTRIBUTE_DIRECTORY) != 0;
            if (isDirectory == directories) {
                if (out.size() >= MAXIMUM_FILES) throw new ExtractException("Xbox directory exceeds import limit (4096 entries).");
                out.add(new Entry(name, table.getInt(at + 4) & 0xFFFFFFFFL, table.getInt(at + 8) & 0xFFFFFFFFL));
            }
            if (right != 0) pending.push(right);
            if (left != 0) pending.push(left);
        }
    }

    private void extract(File destination, Progress progress) throws IOException {
        long[] root = findVolume();

        /* the root's maps folder */
        ByteBuffer table = readDirectory(root[0], root[1], "The disc image's file system is damaged.");
        List<Entry> directories = new ArrayList<>();
        walk(table, true, directories);
        Entry maps = null;
        for (Entry entry : directories) {
            if (entry.name.equalsIgnoreCase("maps")) {
                if (maps != null) throw new ExtractException("Duplicate maps folders in Xbox image.");
                maps = entry;
            }
        }
        if (maps == null)
            throw new ExtractException("The disc image has no maps folder: it is not a Halo disc.");

        /* its files */
        table = readDirectory(maps.sector, maps.size, "The disc image's maps folder is damaged.");
        List<Entry> files = new ArrayList<>();
        walk(table, false, files);
        long total = 0;
        java.util.Set<String> unique=new java.util.HashSet<>();
        boolean hasUi = false;
        for (Entry file : files) {
            total += file.size;
            if(total>12L*1024*1024*1024||!unique.add(file.name))throw new ExtractException("Oversized image data or duplicate filenames");
            if(partition+file.sector*SECTOR_SIZE+file.size>image.size())throw new ExtractException("Truncated disc image");
            hasUi |= file.name.equalsIgnoreCase("ui.map");
        }
        if (!hasUi)
            throw new ExtractException("The disc image's maps folder has no ui.map: it is not a Halo disc.");

        File partial = new File(destination, "maps.partial");
        File finished = new File(destination, "maps");
        if (!partial.isDirectory() && !partial.mkdirs())
            throw new ExtractException("Could not create " + partial + ".");
        ByteBuffer buffer = ByteBuffer.allocateDirect(COPY_BUFFER_SIZE);
        long done = 0;
        for (Entry file : files) {
            File path = new File(partial, file.name);
            long offset = partition + file.sector * SECTOR_SIZE;
            long remaining = file.size;

            try (FileOutputStream out = new FileOutputStream(path)) {
                FileChannel output = out.getChannel();

                while (remaining > 0) {
                    buffer.clear();
                    buffer.limit((int) Math.min(remaining, COPY_BUFFER_SIZE));
                    readAt(offset, buffer);
                    int count = buffer.remaining();
                    while (buffer.hasRemaining())
                        output.write(buffer);
                    offset += count;
                    remaining -= count;
                    done += count;
                    progress.report(file.name, done, total);
                }
            } catch (java.io.InterruptedIOException e) {
                throw e;
            } catch (ExtractException e) {
                throw new ExtractException("Could not read " + file.name + ": " + e.getMessage());
            } catch (IOException e) {
                throw new ExtractException("Could not write " + path + " (is the storage full?).");
            }
        }

        /* (the maps folder may be there, empty: the app makes it for adb) */
        if (!finished.isDirectory() && !finished.mkdirs())
            throw new ExtractException("Could not create " + finished + ".");
        /* Publish ui.map last: haveData() uses it as the completion marker. */
        files.sort(java.util.Comparator.comparing(file -> file.name.equals("ui.map")));
        for (Entry file : files) {
            File from = new File(partial, file.name);
            File to = new File(finished, file.name);

            to.delete();
            if (!from.renameTo(to))
                throw new ExtractException("Could not move " + file.name + " into " + finished + ".");
        }
        partial.delete();
    }
}
