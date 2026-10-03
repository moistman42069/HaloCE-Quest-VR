package com.halo.decomp;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.io.FilterInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Mods made of Halo Custom Edition campaign maps, which replace the
 * campaign's own: downloaded, swapped in with the originals kept aside, and
 * swapped back out.
 *
 * Under the game's data root (the folder holding maps/):
 * <ul>
 * <li>mods/&lt;mod&gt;/maps: the mod's maps while it is not in, and their
 * converted sounds (&lt;map&gt;.map.audio, which the game writes beside a
 * Custom Edition map the first time it loads it,
 * port/linux/game/custom_edition_cache.c);</li>
 * <li>mods/original: the campaign maps the mod's took the place of;</li>
 * <li>mods/&lt;mod&gt;.on while the mod is in, and mods/custom_edition.on,
 * which has the game load Custom Edition maps
 * (port/android/host/host_main.c).</li>
 * </ul>
 * Maps move between those folders by renaming, on one file system, so
 * swapping is instant and nothing is stored twice.
 */
final class ModInstaller {
    interface Progress {
        void report(String text, int permille);
    }

    /** A map of a mod: its file, halomaps.org's file id, its exact size. */
    static final class ModMap {
        final String name;
        final int fid;
        final long size;

        ModMap(String name, int fid, long size) {
            this.name = name;
            this.fid = fid;
            this.size = size;
        }
    }

    static final class Mod {
        final String id;
        final String title;
        final String description;
        final ModMap[] maps;

        Mod(String id, String title, String description, ModMap[] maps) {
            this.id = id;
            this.title = title;
            this.description = description;
            this.maps = maps;
        }

        long totalBytes() {
            long total = 0;
            for (ModMap map : maps)
                total += map.size;
            return total;
        }
    }

    /**
     * SPV1: the Custom Mapping Team's single player campaign for Halo Custom
     * Edition (2006), from halomaps.org ("CMT Version - Single Player"
     * levels). Its maps are "protected", which the game's Custom Edition
     * loader undoes (cache_file_formats.c), and keep most sounds as Ogg
     * Vorbis, which the game converts the first time each level loads.
     */
    static final Mod SPV1 = new Mod("spv1", "SPV1 - CMT Single Player Campaign",
        // (counted from the maps' tags against the original levels': weapons,
        // vehicles, AI characters)
        "The Custom Mapping Team's 2006 remake of all ten campaign levels, made for Halo Custom Edition.\n\n"
            + "• New weapons: about twice the kinds in every level (29 on Halo, where the original has 10)\n"
            + "• New and redesigned enemies and characters, with more kinds in every level\n"
            + "• Many more vehicles (17 on Halo against 6, 23 on The Silent Cartographer against 7, "
            + "and vehicles in The Library)\n"
            + "• Added detail to the levels' environments, and visual changes throughout\n\n"
            + "Download: about 960 MB from halomaps.org; 2.2 GB once installed, and up to 1.1 GB more as "
            + "each level converts its sounds the first time it loads (a minute or two, once). Needs Halo "
            + "Custom Edition's own bitmaps.map, sounds.map and loc.map. Restoring puts the original "
            + "campaign back; SPV1 stays downloaded to switch back in at once.",
        new ModMap[] {
            new ModMap("a10", 1921, 264601050L),
            new ModMap("a30", 1920, 202016403L),
            new ModMap("a50", 1919, 206788649L),
            new ModMap("b30", 1918, 201578087L),
            new ModMap("b40", 1917, 265311261L),
            new ModMap("c10", 1916, 231297155L),
            new ModMap("c20", 1915, 164865081L),
            new ModMap("c40", 1914, 247495074L),
            new ModMap("d20", 1913, 183851031L),
            new ModMap("d40", 1912, 264367517L),
        });

    private static final String DETAIL_URL = "https://www.halomaps.org/hce/detail.cfm";
    private static final String USER_AGENT = "Mozilla/5.0 (Android; Halo CE VR launcher)";
    private static final Pattern HASH = Pattern.compile("name=\"hash\" value=\"([0-9A-Fa-f]{32})\"");

    private final File root;

    ModInstaller(File root) {
        this.root = root;
    }

    private File modsDirectory() {
        return new File(root, "mods");
    }

    private File modMaps(Mod mod) {
        return new File(new File(modsDirectory(), mod.id), "maps");
    }

    private File originals() {
        return new File(modsDirectory(), "original");
    }

    private File gameMaps() {
        return new File(root, "maps");
    }

    private File marker(Mod mod) {
        return new File(modsDirectory(), mod.id + ".on");
    }

    private File pendingMarker(Mod mod) {
        return new File(modsDirectory(), mod.id + ".changing");
    }

    boolean recoveryNeeded(Mod mod) {
        return pendingMarker(mod).isFile();
    }

    private File customEditionMarker() {
        return new File(modsDirectory(), "custom_edition.on");
    }

    boolean installed(Mod mod) {
        return marker(mod).isFile() || recoveryNeeded(mod);
    }

    // ---------- Halo Custom Edition's resource maps

    /**
     * Custom Edition maps take some of their textures' pixels and sounds'
     * samples from Custom Edition's own bitmaps.map, sounds.map and loc.map,
     * which come with the game (not with the mods, and not with the Xbox's
     * data): the player brings them once, from a Custom Edition installation's
     * maps folder (its stock ones), into mods/ce. Their headers' first word
     * says which they are.
     */
    static final String[] RESOURCE_NAMES = { "bitmaps", "sounds", "loc" };

    /**
     * The original resource maps' sizes, as Halo Custom Edition installs
     * them (its patches leave them alone). Custom Edition maps name their
     * resources by index into these exact files: a modified bitmaps.map
     * (Halo Refined's, say) loads, but shows the wrong textures, so only
     * the original is taken.
     */
    static final long[] RESOURCE_SIZES = { 123547749L, 41718640L, 391996L };

    /** "117.8 MB" and the like. */
    static String megabytes(long bytes) {
        return String.format(java.util.Locale.ROOT, "%.1f MB", bytes / 1048576.0);
    }

    /** Whether a resource map of that type is the original, by its size. */
    static boolean resourceOriginal(int type, long size) {
        return size == RESOURCE_SIZES[type - 1];
    }

    private File resourceDirectory() {
        return new File(modsDirectory(), "ce");
    }

    /** The resource map type (1 bitmaps, 2 sounds, 3 loc) of a file's first bytes, or 0. */
    static int resourceType(byte[] header) {
        if (header.length < 4)
            return 0;
        int type = (header[0] & 0xff) | ((header[1] & 0xff) << 8) | ((header[2] & 0xff) << 16) | ((header[3] & 0xff) << 24);
        return type >= 1 && type <= 3 ? type : 0;
    }

    /** Where a resource map of that type is kept (whether or not it is there). */
    File resourceFile(int type) {
        return new File(resourceDirectory(), RESOURCE_NAMES[type - 1] + ".map");
    }

    /** The resource map of that type the mods have (kept aside, or in the game's maps), or null. */
    private File presentResource(int type) {
        File kept = resourceFile(type);
        File game = new File(gameMaps(), RESOURCE_NAMES[type - 1] + ".map");

        return kept.isFile() ? kept : game.isFile() ? game : null;
    }

    /** Every resource map present, and the original. */
    boolean haveResources() {
        for (int type = 1; type <= 3; type++) {
            File file = presentResource(type);

            if (file == null || !resourceOriginal(type, file.length()))
                return false;
        }
        return true;
    }

    /** What is still wanted of the resource maps, for the player. */
    String missingResources() {
        StringBuilder missing = new StringBuilder();

        for (int type = 1; type <= 3; type++) {
            File file = presentResource(type);
            String name = RESOURCE_NAMES[type - 1] + ".map";

            if (file == null)
                missing.append(missing.length() > 0 ? ", " : "").append(name);
            else if (!resourceOriginal(type, file.length()))
                missing.append(missing.length() > 0 ? ", " : "").append(name).append(" (the one there is ")
                    .append(megabytes(file.length())).append(", not the original's ")
                    .append(megabytes(RESOURCE_SIZES[type - 1])).append(")");
        }
        return missing.toString();
    }

    /** The resource maps go in with a Custom Edition mod, and out with it. */
    private void resourcesIn() throws IOException {
        for (int type = 1; type <= 3; type++) {
            File game = new File(gameMaps(), RESOURCE_NAMES[type - 1] + ".map");
            File original = new File(originals(), RESOURCE_NAMES[type - 1] + ".map");

            if (!resourceFile(type).isFile())
                continue;
            if (game.exists() && !original.exists())
                move(game, original);
            move(resourceFile(type), game);
        }
    }

    private void resourcesOut() throws IOException {
        File directory = resourceDirectory();

        if (!directory.isDirectory() && !directory.mkdirs())
            throw new IOException("cannot make " + directory);
        for (int type = 1; type <= 3; type++) {
            File game = new File(gameMaps(), RESOURCE_NAMES[type - 1] + ".map");
            File original = new File(originals(), RESOURCE_NAMES[type - 1] + ".map");

            if (game.exists() && !resourceFile(type).exists())
                move(game, resourceFile(type));
            if (original.exists())
                move(original, game);
        }
    }

    /** Where the player can put the resource maps with a computer instead. */
    String resourcePath() {
        return resourceDirectory().getAbsolutePath();
    }

    File resourceDirectoryMade() throws IOException {
        File directory = resourceDirectory();

        if (!directory.isDirectory() && !directory.mkdirs())
            throw new IOException("cannot make " + directory);
        return directory;
    }

    /** Every map of the mod downloaded whole (in or out of the game). */
    boolean downloaded(Mod mod) {
        for (ModMap map : mod.maps) {
            File out = new File(modMaps(mod), map.name + ".map");
            File in = new File(gameMaps(), map.name + ".map");
            boolean whole = (out.isFile() && out.length() == map.size) ||
                (installed(mod) && in.isFile() && in.length() == map.size);
            if (!whole)
                return false;
        }
        return true;
    }

    /** Include interrupted downloads so the launcher can offer cleanup. */
    boolean hasDownloadFiles(Mod mod) {
        File directory = modMaps(mod);
        for (ModMap map : mod.maps) {
            if (new File(directory, map.name + ".map").exists()
                    || new File(directory, map.name + ".map.part").exists()
                    || new File(directory, map.name + ".map.audio").exists()) return true;
        }
        return false;
    }

    /** Downloads what is missing, then swaps the mod's maps in. */
    void install(Mod mod, Progress progress) throws IOException {
        File maps = modMaps(mod);
        long total = mod.totalBytes(), done = 0;

        if (installed(mod))
            return;
        if (!haveResources())
            throw new IOException("Custom Edition's resource maps are needed first (" + missingResources() + ")");
        if (!maps.isDirectory() && !maps.mkdirs())
            throw new IOException("cannot make " + maps);
        for (int index = 0; index < mod.maps.length; index++) {
            ModMap map = mod.maps[index];
            File file = new File(maps, map.name + ".map");

            if (!(file.isFile() && file.length() == map.size))
                download(map, file, index, mod.maps.length, done, total, progress);
            done += map.size;
        }
        progress.report("Swapping the campaign's maps for " + mod.title + "...", 1000);
        swapIn(mod);
    }

    private void download(ModMap map, File file, int index, int count, long done, long total, Progress progress)
        throws IOException {
        String label = "Downloading " + map.name + " (" + (index + 1) + " of " + count + ")";
        String detail = DETAIL_URL + "?fid=" + map.fid;
        File partial = new File(file.getPath() + ".part");

        progress.report(label + "...", (int) (done * 1000 / total));
        String page = get(detail);
        Matcher matcher = HASH.matcher(page);
        if (!matcher.find())
            throw new IOException("halomaps.org's page for " + map.name + " has no download");

        HttpURLConnection connection = (HttpURLConnection) new URL(DETAIL_URL).openConnection();
        connection.setRequestMethod("POST");
        connection.setDoOutput(true);
        connection.setConnectTimeout(30000);
        connection.setReadTimeout(60000);
        connection.setRequestProperty("User-Agent", USER_AGENT);
        connection.setRequestProperty("Referer", detail);
        connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        try (OutputStream out = connection.getOutputStream()) {
            out.write(("fid=" + map.fid + "&action=dl&hash=" + matcher.group(1) + "&submit=download")
                .getBytes(StandardCharsets.US_ASCII));
        }
        if (connection.getResponseCode() != 200)
            throw new IOException("halomaps.org answered " + connection.getResponseCode() + " for " + map.name);

        // the archive is read as it arrives, its map written straight out
        try (CountingStream counted = new CountingStream(new BufferedInputStream(connection.getInputStream()));
             ZipInputStream zip = new ZipInputStream(counted)) {
            long archive = connection.getContentLengthLong();
            ZipEntry entry;
            boolean found = false;

            while ((entry = zip.getNextEntry()) != null) {
                String name = new File(entry.getName()).getName();

                if (!name.equalsIgnoreCase(map.name + ".map"))
                    continue;
                found = true;
                try (OutputStream out = new FileOutputStream(partial)) {
                    byte[] buffer = new byte[1 << 16];
                    long written = 0, reported = 0;
                    int read;

                    while ((read = zip.read(buffer)) > 0) {
                        out.write(buffer, 0, read);
                        written += read;
                        if (written - reported > (4 << 20)) {
                            reported = written;
                            long fraction = archive > 0 ? counted.count * map.size / archive : written;
                            progress.report(label + ": " + (counted.count >> 20) + " of "
                                    + (archive > 0 ? (archive >> 20) + " MB" : "? MB"),
                                (int) ((done + Math.min(fraction, map.size)) * 1000 / total));
                        }
                    }
                }
                break;
            }
            if (!found)
                throw new IOException("the download of " + map.name + " holds no " + map.name + ".map");
        } finally {
            connection.disconnect();
        }
        if (partial.length() != map.size) {
            long size = partial.length();
            partial.delete();
            throw new IOException(map.name + ".map is " + size + " bytes, not the " + map.size + " expected");
        }
        if (!partial.renameTo(file))
            throw new IOException("cannot keep " + file);
    }

    private static String get(String address) throws IOException {
        HttpURLConnection connection = (HttpURLConnection) new URL(address).openConnection();
        connection.setConnectTimeout(30000);
        connection.setReadTimeout(60000);
        connection.setRequestProperty("User-Agent", USER_AGENT);
        try (InputStream in = connection.getInputStream()) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            byte[] buffer = new byte[1 << 14];
            int read;

            while ((read = in.read(buffer)) > 0)
                bytes.write(buffer, 0, read);
            return bytes.toString("ISO-8859-1");
        } finally {
            connection.disconnect();
        }
    }

    private static void move(File from, File to) throws IOException {
        if (!from.exists())
            return;
        // Same-filesystem atomic replacement: a failed move must not first
        // delete the only surviving destination copy.
        Files.move(from.toPath(), to.toPath(), StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING);
    }

    /** The originals aside, the mod's maps (and their converted sounds) in. */
    private void swapIn(Mod mod) throws IOException {
        File originals = originals();

        if (!originals.isDirectory() && !originals.mkdirs())
            throw new IOException("cannot make " + originals);
        for (ModMap map : mod.maps) {
            if (!new File(originals, map.name + ".map").isFile()
                    && !isXboxMap(new File(gameMaps(), map.name + ".map")))
                throw new IOException("original Xbox campaign map missing: " + map.name);
        }
        touch(pendingMarker(mod));
        for (ModMap map : mod.maps) {
            File game = new File(gameMaps(), map.name + ".map");
            File original = new File(originals, map.name + ".map");

            // (an original already aside stays; the game's file is then a
            // mod's, from an interrupted swap)
            if (!original.exists())
                move(game, original);
            move(new File(modMaps(mod), map.name + ".map"), game);
            move(new File(modMaps(mod), map.name + ".map.audio"), new File(gameMaps(), map.name + ".map.audio"));
        }
        resourcesIn();
        touch(marker(mod));
        touch(customEditionMarker());
        deleteChecked(pendingMarker(mod));
    }

    /** The mod's maps out (kept, to go back in at once), the originals back. */
    void restore(Mod mod, Progress progress) throws IOException {
        File maps = modMaps(mod);

        progress.report("Putting the original campaign back...", 0);
        // A retry after an interrupted restore may already have returned a
        // stock map. Missing backup + a mod still active is not success.
        for (ModMap map : mod.maps) {
            File original = new File(originals(), map.name + ".map");
            if (!original.isFile() && !isXboxMap(new File(gameMaps(), map.name + ".map")))
                throw new IOException("original backup missing for " + map.name
                        + "; mod files kept. Restore this map from your original Halo disc before retrying.");
        }
        touch(pendingMarker(mod));
        if (!maps.isDirectory() && !maps.mkdirs())
            throw new IOException("cannot make " + maps);
        for (ModMap map : mod.maps) {
            File game = new File(gameMaps(), map.name + ".map");
            File original = new File(originals(), map.name + ".map");

            if (original.exists()) {
                move(game, new File(maps, map.name + ".map"));
                move(new File(gameMaps(), map.name + ".map.audio"), new File(maps, map.name + ".map.audio"));
                move(original, game);
            }
        }
        resourcesOut();
        deleteChecked(customEditionMarker());
        deleteChecked(marker(mod));
        deleteChecked(pendingMarker(mod));
        progress.report("The original campaign is back.", 1000);
    }

    private static boolean isXboxMap(File file) throws IOException {
        if (!file.isFile()) return false;
        byte[] header = new byte[8];
        try (InputStream in = new FileInputStream(file)) {
            int read = 0, count;
            while (read < header.length && (count = in.read(header, read, header.length - read)) > 0)
                read += count;
            // Cache header 'head', little-endian fourcc, version 5 (Xbox).
            return read == 8 && header[0] == 'd' && header[1] == 'a'
                    && header[2] == 'e' && header[3] == 'h'
                    && header[4] == 5 && header[5] == 0 && header[6] == 0 && header[7] == 0;
        }
    }

    private static void deleteChecked(File file) throws IOException {
        if (file.exists() && !file.delete()) throw new IOException("cannot delete " + file);
    }

    /** Uninstall restores first; a restoration failure never deletes the mod. */
    void delete(Mod mod, Progress progress) throws IOException {
        if (installed(mod)) restore(mod, progress);
        File[] files = modMaps(mod).listFiles();
        if (files == null && modMaps(mod).exists())
            throw new IOException("cannot list downloaded maps in " + modMaps(mod));
        if (files != null) for (File file : files) {
            // Delete only files owned by this mod, never originals/CE resources
            // or an unexpected directory supplied by the user.
            for (ModMap map : mod.maps) {
                String name = file.getName();
                if (name.equals(map.name + ".map") || name.equals(map.name + ".map.audio")
                        || name.equals(map.name + ".map.part")) {
                    if (file.isDirectory()) throw new IOException("unexpected directory: " + file);
                    deleteChecked(file);
                    break;
                }
            }
        }
        progress.report("Original campaign restored; downloaded mod maps removed.", 1000);
    }

    private static void touch(File file) throws IOException {
        File parent = file.getParentFile();

        if (parent != null && !parent.isDirectory())
            parent.mkdirs();
        try (OutputStream out = new FileOutputStream(file)) {
            out.write('\n');
        }
    }

    /** Counts the bytes read through it (the archive's, for progress). */
    private static final class CountingStream extends FilterInputStream {
        long count;

        CountingStream(InputStream in) {
            super(in);
        }

        @Override
        public int read() throws IOException {
            int value = super.read();
            if (value >= 0)
                count++;
            return value;
        }

        @Override
        public int read(byte[] buffer, int offset, int length) throws IOException {
            int read = super.read(buffer, offset, length);
            if (read > 0)
                count += read;
            return read;
        }
    }
}
