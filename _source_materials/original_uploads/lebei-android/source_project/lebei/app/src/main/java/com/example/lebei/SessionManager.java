package com.example.lebei;

import android.content.Context;
import android.content.SharedPreferences;
import com.example.lebei.api.UserProfile;
import com.google.gson.Gson;

public class SessionManager {
    private static final String PREF_NAME = "user_session";
    private static final String KEY_USERNAME = "username";
    private static final String KEY_TOKEN = "token";
    private static final String KEY_PROFILE_JSON = "profile_json";
    /** 上次写入本地 Room 学习数据的账号 id；登出时保留，用于下次登录判断是否换号 */
    private static final String KEY_LAST_LOCAL_USER_ID = "last_local_user_id";

    private final SharedPreferences prefs;
    private final Context appContext;
    private static final Gson GSON = new Gson();

    public SessionManager(Context context) {
        this.appContext = context.getApplicationContext();
        prefs = this.appContext.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    public void saveSession(String token, UserProfile profile) {
        long prevLocalUserId = prefs.getLong(KEY_LAST_LOCAL_USER_ID, -1L);
        SharedPreferences.Editor ed =
                prefs.edit()
                        .putString(KEY_TOKEN, token)
                        .putString(KEY_USERNAME, profile != null ? profile.username : null)
                        .putString(KEY_PROFILE_JSON, profile != null ? GSON.toJson(profile) : null);
        if (profile != null) {
            long newId = profile.id;
            if (prevLocalUserId != -1L && prevLocalUserId != newId) {
                LocalLearningDataStore.clearForNewUser(appContext);
            }
            ed.putLong(KEY_LAST_LOCAL_USER_ID, newId);
        } else {
            ed.remove(KEY_LAST_LOCAL_USER_ID);
        }
        ed.apply();
    }

    public void saveUsername(String username) {
        prefs.edit().putString(KEY_USERNAME, username).apply();
    }

    public void saveProfile(UserProfile profile) {
        if (profile == null) {
            prefs.edit().remove(KEY_PROFILE_JSON).apply();
            return;
        }
        long prevLocalUserId = prefs.getLong(KEY_LAST_LOCAL_USER_ID, -1L);
        long newId = profile.id;
        if (prevLocalUserId != -1L && prevLocalUserId != newId) {
            LocalLearningDataStore.clearForNewUser(appContext);
        }
        SharedPreferences.Editor ed =
                prefs.edit().putString(KEY_PROFILE_JSON, GSON.toJson(profile)).putLong(KEY_LAST_LOCAL_USER_ID, newId);
        if (profile.username != null) {
            ed.putString(KEY_USERNAME, profile.username);
        }
        ed.apply();
    }

    public String getUsername() {
        return prefs.getString(KEY_USERNAME, null);
    }

    public String getToken() {
        return prefs.getString(KEY_TOKEN, null);
    }

    public UserProfile getProfile() {
        String json = prefs.getString(KEY_PROFILE_JSON, null);
        if (json == null) {
            return null;
        }
        try {
            return GSON.fromJson(json, UserProfile.class);
        } catch (Exception e) {
            return null;
        }
    }

    public boolean isLoggedIn() {
        return getToken() != null;
    }

    /** 清除登录态；保留 {@link #KEY_LAST_LOCAL_USER_ID} 以便下次登录检测换号并清空本地学习数据。 */
    public void logout() {
        prefs.edit()
                .remove(KEY_TOKEN)
                .remove(KEY_USERNAME)
                .remove(KEY_PROFILE_JSON)
                .apply();
    }
}
