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

## Quest OS v78: tracked hand and weapon orientation

**Status:** follow-up report; the latest weapon/two-hand symptom is not reproduced or tied to a confirmed APK build yet.

### Report

Sophia SPRKLZ previously reported on 2026-09-28 that their hands were rotated 180 degrees in VR and attributed it to Quest OS v78. They said similar behavior had occurred in both HL2 ports and that hand offsets might help. In the Halo CE thread on 2026-10-04, shortly after the 1.0.2 release post, they reported that the orientation option made the hands upright while weapons stayed upside down; they thanked the project for adding that option. They then reported that the weapon returns to an upside-down orientation when held with two hands.

The sequence points to a possible difference between hand and weapon orientation transforms, with the two-hand grip path potentially overriding or recomputing weapon orientation. This is a lead, not a confirmed code-level cause. The new Halo CE messages do not state the headset model, active OS version, APK version, handedness, weapon type, or exact grip settings. The user's earlier v78 report was in a different project thread; do not treat this alone as proof that the current Halo CE behavior is specific to v78. The older thread identifies Sophia as using a Quest 3S and says they were on v78, but that hardware/version pairing was not repeated with the Halo CE report.

Source messages: [prior 180-degree hand report and v78 attribution](https://discord.com/channels/747967102895390741/1551995761313583244/1554131147984863405), [v78 explanation](https://discord.com/channels/747967102895390741/1551995761313583244/1554134889685590109), [hands upright but weapons upside down](https://discord.com/channels/747967102895390741/1555959498349215774/1556346207398535240), and [two-hand grip returns weapon to upside down](https://discord.com/channels/747967102895390741/1555959498349215774/1556346207398535240) in the Flat2VR Modding Discord.

### Follow-up before changing orientation code

1. Confirm the exact headset, Quest OS version, APK version/code, handedness, weapon, orientation setting, and whether two-hand grip is enabled.
2. Reproduce with one-handed and two-handed weapons, comparing hand-only, weapon-only, and combined orientation adjustments. Check whether the two-hand support-hand pose and weapon transform use the same coordinate convention and apply the orientation correction exactly once.
3. Keep the fix localized to the transform path that fails. Verify tracked hands, primary-hand weapon alignment, support-hand lock, reload/grenade animation handoff, and stock/no-VR behavior; do not disturb previously accepted action blending or grip behavior without a reproducer.
4. Test on Quest OS v78 and a current supported OS if available. Record the APK identity and sanitized logs/video for both results. Until then, describe v78 as a reported correlation, not a confirmed incompatibility.

### Suggested future release note

> **Quest controller orientation follow-up:** a tester who previously reported 180-degree hand rotation on Quest OS v78 says the hand-orientation option makes hands upright, but weapons remain upside down and two-hand grip restores the inverted weapon orientation. The exact Halo CE device/OS/build and settings are unconfirmed. Verify hand, weapon, and two-hand transform paths independently on v78 and a current OS before claiming the issue is fixed or v78-specific.
