package com.example.lebei;

import android.content.Context;
import android.content.SharedPreferences;
import androidx.appcompat.app.AlertDialog;

public final class PageGuideDialog {

    private static final String PREFS = "page_guides";

    private PageGuideDialog() {}

    public static void showOnce(Context context, String key, String title, String message) {
        if (context == null) {
            return;
        }
        SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String prefKey = "shown_" + key;
        if (prefs.getBoolean(prefKey, false)) {
            return;
        }
        prefs.edit().putBoolean(prefKey, true).apply();
        show(context, title, message);
    }

    public static void show(Context context, String title, String message) {
        if (context == null) {
            return;
        }
        new AlertDialog.Builder(context)
                .setTitle(title)
                .setMessage(message)
                .setPositiveButton("知道了", null)
                .show();
    }
}
