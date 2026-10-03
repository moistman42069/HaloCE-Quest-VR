package com.halo.decomp;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

/** Host-side filesystem checks; never reads or edits installed game data. */
public final class ModInstallerRestoreTest {
    private static final ModInstaller.Mod MOD = new ModInstaller.Mod("fixture", "Fixture", "",
            new ModInstaller.ModMap[]{new ModInstaller.ModMap("a10", 0, 16), new ModInstaller.ModMap("a30", 0, 16)});
    private static final byte[] STOCK = {'d', 'a', 'e', 'h', 5, 0, 0, 0, 11};
    private static final byte[] MODDED = {'d', 'a', 'e', 'h', 97, 2, 0, 0, 22};
    private static final ModInstaller.Progress QUIET = (text, value) -> {};

    private static void put(Path root, String relative, byte[] bytes) throws IOException {
        Path file = root.resolve(relative);
        Files.createDirectories(file.getParent());
        Files.write(file, bytes);
    }
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    private static Path fixture(Path parent, String name) throws IOException {
        Path root = Files.createDirectory(parent.resolve(name));
        put(root, "mods/fixture.on", new byte[]{1});
        put(root, "mods/custom_edition.on", new byte[]{1});
        for (String map : new String[]{"a10", "a30"}) {
            put(root, "maps/" + map + ".map", MODDED);
            put(root, "mods/original/" + map + ".map", STOCK);
        }
        return root;
    }
    public static void main(String[] args) throws Exception {
        Path parent = Path.of(args[0]);
        Files.createDirectories(parent);
        Path root = fixture(parent, "uninstall");
        put(root, "maps/bitmaps.map", new byte[]{1, 2, 3});
        put(root, "mods/original/bitmaps.map", new byte[]{4, 5});
        put(root, "maps/a10.map.audio", new byte[]{6});
        put(root, "mods/fixture/maps/user-note.txt", new byte[]{7});
        ModInstaller installer = new ModInstaller(root.toFile());
        installer.delete(MOD, QUIET);
        require(!installer.installed(MOD), "active mod marker remains");
        for (String map : new String[]{"a10", "a30"}) {
            require(Arrays.equals(Files.readAllBytes(root.resolve("maps/" + map + ".map")), STOCK), "stock map not restored");
            require(!Files.exists(root.resolve("mods/fixture/maps/" + map + ".map")), "download not deleted");
        }
        require(!Files.exists(root.resolve("maps/a10.map.audio")), "mod audio remains active");
        require(Arrays.equals(Files.readAllBytes(root.resolve("maps/bitmaps.map")), new byte[]{4,5}), "stock resource not restored");
        require(Files.exists(root.resolve("mods/ce/bitmaps.map")), "shared CE resource lost");
        require(Files.exists(root.resolve("mods/fixture/maps/user-note.txt")), "unowned file deleted");
        installer.delete(MOD, QUIET); // Idempotent delete.

        root = fixture(parent, "missing-backup");
        Files.delete(root.resolve("mods/original/a30.map"));
        boolean refused = false;
        try { new ModInstaller(root.toFile()).delete(MOD, QUIET); }
        catch (IOException expected) { refused = true; }
        require(refused, "missing backup silently accepted");
        require(Files.exists(root.resolve("mods/original/a10.map")), "preflight modified other backups");
        require(Arrays.equals(Files.readAllBytes(root.resolve("maps/a10.map")), MODDED), "preflight modified game maps");
        require(Files.exists(root.resolve("mods/fixture.on")), "failure cleared active marker");

        root = fixture(parent, "partial-restore");
        Files.delete(root.resolve("mods/original/a10.map"));
        put(root, "maps/a10.map", STOCK);
        put(root, "mods/fixture/maps/a10.map", MODDED);
        new ModInstaller(root.toFile()).delete(MOD, QUIET);
        require(Arrays.equals(Files.readAllBytes(root.resolve("maps/a10.map")), STOCK), "retry moved restored stock away");
        require(Arrays.equals(Files.readAllBytes(root.resolve("maps/a30.map")), STOCK), "retry did not finish restore");
        root = fixture(parent, "interrupted-install");
        Files.delete(root.resolve("mods/fixture.on"));
        put(root, "mods/fixture.changing", new byte[]{1});
        installer = new ModInstaller(root.toFile());
        require(installer.installed(MOD) && installer.recoveryNeeded(MOD), "unfinished install not recoverable");
        installer.delete(MOD, QUIET);
        require(!installer.recoveryNeeded(MOD), "recovery marker not cleared");
        require(Arrays.equals(Files.readAllBytes(root.resolve("maps/a10.map")), STOCK), "interrupted install lost original");
        System.out.println("PASS: active uninstall, resources/audio, unowned-file preservation, repeat delete, missing-backup refusal, interrupted-restore retry");
    }
}
