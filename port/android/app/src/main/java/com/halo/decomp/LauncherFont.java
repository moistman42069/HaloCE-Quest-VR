package com.halo.decomp;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Typeface;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import java.util.WeakHashMap;

/** Optional display type for short launcher labels; long instructions keep Android's readable sans font. */
final class LauncherFont {
    private static final String PREFS = "launcher_appearance";
    private static final String KEY_HALO_FONT = "halo_inspired_font";
    private static final int MAX_DISPLAY_TEXT_LENGTH = 64;
    private static Typeface haloTypeface;
    private static final WeakHashMap<TextView, Typeface> originalTypefaces = new WeakHashMap<>();
    private static final WeakHashMap<TextView, Boolean> normalLabels = new WeakHashMap<>();

    private LauncherFont() { }

    static boolean isHaloEnabled(Context context) {
        return preferences(context).getBoolean(KEY_HALO_FONT, true);
    }

    static void toggle(Context context) {
        SharedPreferences prefs = preferences(context);
        prefs.edit().putBoolean(KEY_HALO_FONT, !isHaloEnabled(context)).apply();
    }

    static String toggleLabel(Context context) {
        return isHaloEnabled(context)
            ? "Font: Halo (tap for normal)"
            : "Font: normal (tap for Halo)";
    }

    static void apply(Context context, View root) {
        applyToShortLabels(root, isHaloEnabled(context) ? typeface(context) : null);
    }

    /** Dynamic status text stays readable even when its initial value is short or empty. */
    static void keepNormal(TextView text) {
        if (text == null)
            return;
        normalLabels.put(text, Boolean.TRUE);
        if (originalTypefaces.containsKey(text))
            text.setTypeface(originalTypefaces.get(text));
    }

    private static SharedPreferences preferences(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    private static Typeface typeface(Context context) {
        if (haloTypeface != null)
            return haloTypeface;
        try {
            haloTypeface = Typeface.createFromAsset(context.getAssets(), "fonts/Orbitron-Regular.ttf");
        } catch (RuntimeException error) {
            RunLog.line("Launcher Halo-inspired font unavailable; using Android default: "
                + error.getClass().getSimpleName());
        }
        return haloTypeface;
    }

    private static void applyToShortLabels(View view, Typeface face) {
        if (view instanceof TextView) {
            TextView text = (TextView) view;
            CharSequence value = text.getText();
            boolean shortLabel = value != null && value.length() <= MAX_DISPLAY_TEXT_LENGTH;
            if (face == null || normalLabels.containsKey(text) || !shortLabel) {
                if (originalTypefaces.containsKey(text)) {
                    Typeface original = originalTypefaces.get(text);
                    text.setTypeface(original);
                }
            } else {
                Typeface original = originalTypefaces.get(text);
                if (!originalTypefaces.containsKey(text)) {
                    original = text.getTypeface();
                    originalTypefaces.put(text, original);
                }
                int style = original == null ? Typeface.NORMAL : original.getStyle();
                text.setTypeface(Typeface.create(face, style));
            }
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++)
                applyToShortLabels(group.getChildAt(i), face);
        }
    }
}
