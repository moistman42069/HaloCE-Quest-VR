# Future release follow-ups

## Quest 1: `.xiso` import rejected after phone-to-headset transfer

**Status:** unresolved report; reproduction and device/build identity are not yet confirmed.

### Report

A Quest 1 tester reported in the Flat2VR Modding `new-vr-mods` Halo CE thread on 2026-10-03 that the launcher rejected their `.xiso` with "isn't an Xbox disc image." They said it was the same image they had used on their phone. They later checked it again on the phone with the latest version and said it worked there, suggesting that copying it from the phone to the Quest may have corrupted the transfer. They had used the phone because the source site's CAPTCHA could not be completed in the Quest browser. Later that evening they said it might simply not work on Quest 1, but no evidence established a Quest 1 incompatibility.

The tester did not provide a Quest 1 launch/import log or confirm the exact APK build on the headset. The report therefore does **not** establish that the XISO parser rejects a valid image, that Quest 1 is unsupported, or that transfer corruption was the cause. The later reply is also unverified.

Source messages: [initial import report](https://discord.com/channels/747967102895390741/1555959498349215774/1556108220697808919) and [later Quest 1 comment](https://discord.com/channels/747967102895390741/1555959498349215774/1556139880416022580) in the Flat2VR Halo CE thread.

### Follow-up before claiming a fix or compatibility

1. Identify the exact APK version/code on Quest 1 and the phone, Quest OS version, import method, `.xiso` size, and complete launcher error/log. Do not request or publish the game image itself.
2. Compare SHA-256 of the source image on the phone with the transferred copy on Quest. A different hash confirms the copy changed; matching hashes rule that out as the explanation.
3. With a hash-matched file, test the same build's ISO/XISO importer on Quest 1 and a newer Quest, then compare with a known-good extracted game folder. Preserve the exact sanitized logs.
4. If only Quest 1 fails with identical bytes, inspect the importer/storage and platform failure path before changing format detection. If hashes differ, document the transfer failure separately from XISO support.
5. Record the tested model, OS, APK code, image hash, container type, and result. Do not infer general Quest 1 VR performance/support from a data-import test.

### Suggested future release note

> **Quest 1 game-data import:** one tester reported that a transferred `.xiso` was rejected as an invalid Xbox image on Quest 1, while the same file worked on their phone. The file may have changed during transfer, but no Quest log or hash comparison was provided. Quest 1 import and headset compatibility remain unverified; compare the file hashes and retest before attributing this to a parser or hardware limitation.
