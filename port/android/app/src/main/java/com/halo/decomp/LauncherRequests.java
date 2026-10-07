package com.halo.decomp;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;

/** Retire abandoned one-shot commands before an explicit return to the main menu. */
final class LauncherRequests {
    private LauncherRequests() {}

    static int retire(File gameRoot) throws IOException {
        if (gameRoot == null) throw new IOException("No active game folder.");
        Path root = gameRoot.getCanonicalFile().toPath();
        Path batch = null;
        int moved = 0;
        for (String name : new String[]{"coop_host.txt", "pvp_host.txt", "join_link.txt"}) {
            Path request = root.resolve(name);
            if (!Files.exists(request, LinkOption.NOFOLLOW_LINKS)) continue;
            if (!Files.isRegularFile(request, LinkOption.NOFOLLOW_LINKS))
                throw new IOException("A pending launch request is not a regular file: " + name);
            if (batch == null) {
                Path history = root.resolve("launcher-history");
                if (!history.toFile().getCanonicalFile().toPath().equals(history))
                    throw new IOException("The launch history folder must stay inside the active game folder.");
                Files.createDirectories(history);
                batch = Files.createTempDirectory(history, "requests-");
            }
            try {
                Files.move(request, batch.resolve(name));
                moved++;
            } catch (NoSuchFileException alreadyConsumed) {
                // An already-running game may consume its one-shot request first.
                if (Files.exists(request, LinkOption.NOFOLLOW_LINKS)) throw alreadyConsumed;
            }
        }
        return moved;
    }
}
