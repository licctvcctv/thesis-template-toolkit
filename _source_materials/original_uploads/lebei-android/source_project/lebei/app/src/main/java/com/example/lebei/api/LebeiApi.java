package com.example.lebei.api;

import com.example.lebei.BuildConfig;
import com.example.lebei.SessionManager;
import com.example.lebei.Word;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.reflect.TypeToken;
import java.io.IOException;
import java.lang.reflect.Type;
import java.util.List;
import java.util.concurrent.TimeUnit;
import okhttp3.HttpUrl;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class LebeiApi {

    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    private static final Gson GSON = new Gson();

    private final OkHttpClient client =
            new OkHttpClient.Builder()
                    .connectTimeout(15, TimeUnit.SECONDS)
                    .readTimeout(30, TimeUnit.SECONDS)
                    .writeTimeout(30, TimeUnit.SECONDS)
                    .build();

    private final String baseUrl;

    public LebeiApi() {
        String u = BuildConfig.API_BASE_URL;
        this.baseUrl = u.endsWith("/") ? u.substring(0, u.length() - 1) : u;
    }

    public AuthResponse register(String username, String password) throws IOException {
        JsonObject body = new JsonObject();
        body.addProperty("username", username);
        body.addProperty("password", password);
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/auth/register")
                        .post(RequestBody.create(body.toString(), JSON))
                        .build();
        return executeAuth(request);
    }

    public AuthResponse login(String username, String password) throws IOException {
        JsonObject body = new JsonObject();
        body.addProperty("username", username);
        body.addProperty("password", password);
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/auth/login")
                        .post(RequestBody.create(body.toString(), JSON))
                        .build();
        return executeAuth(request);
    }

    public UserProfile getMe(String token) throws IOException {
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/user/me")
                        .header("Authorization", "Bearer " + token)
                        .get()
                        .build();
        try (Response response = client.newCall(request).execute()) {
            String bodyStr = response.body() != null ? response.body().string() : "";
            if (!response.isSuccessful()) {
                throw new IOException(parseMessage(bodyStr, response.code()));
            }
            return GSON.fromJson(bodyStr, UserProfile.class);
        }
    }

    public UserProfile updateProfile(
            String token,
            int ageGroup,
            String level,
            String currentBookId,
            int dailyNewWords,
            int dailyReviewWords,
            boolean profileComplete)
            throws IOException {
        JsonObject body = new JsonObject();
        body.addProperty("ageGroup", ageGroup);
        body.addProperty("level", level);
        body.addProperty("currentBookId", currentBookId);
        body.addProperty("dailyNewWords", dailyNewWords);
        body.addProperty("dailyReviewWords", dailyReviewWords);
        body.addProperty("profileComplete", profileComplete);
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/user/profile")
                        .header("Authorization", "Bearer " + token)
                        .put(RequestBody.create(body.toString(), JSON))
                        .build();
        return executeUser(request);
    }

    public UserProfile updatePlan(String token, String currentBookId, int dailyNewWords, int dailyReviewWords)
            throws IOException {
        JsonObject body = new JsonObject();
        body.addProperty("currentBookId", currentBookId);
        body.addProperty("dailyNewWords", dailyNewWords);
        body.addProperty("dailyReviewWords", dailyReviewWords);
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/user/plan")
                        .header("Authorization", "Bearer " + token)
                        .put(RequestBody.create(body.toString(), JSON))
                        .build();
        return executeUser(request);
    }

    /** 每完成一个单词学习（简单/困难）调用一次，服务端积分 +1。 */
    public UserProfile recordStudyWord(String token) throws IOException {
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/user/stats/study-word")
                        .header("Authorization", "Bearer " + token)
                        .post(RequestBody.create("{}", JSON))
                        .build();
        return executeUser(request);
    }

    /** 与后台「App 用户学习排行榜」同一数据源，limit 与管理员页默认一致为 100 */
    public List<LeaderboardEntry> getLeaderboard(String token, int limit) throws IOException {
        HttpUrl parsed = HttpUrl.parse(baseUrl + "/api/app/leaderboard");
        if (parsed == null) {
            throw new IOException("无效的 API 地址");
        }
        HttpUrl url = parsed.newBuilder().addQueryParameter("limit", String.valueOf(limit)).build();
        Request request =
                new Request.Builder()
                        .url(url)
                        .header("Authorization", "Bearer " + token)
                        .get()
                        .build();
        try (Response response = client.newCall(request).execute()) {
            String bodyStr = response.body() != null ? response.body().string() : "";
            if (!response.isSuccessful()) {
                throw new IOException(parseMessage(bodyStr, response.code()));
            }
            Type listType = new TypeToken<List<LeaderboardEntry>>() {}.getType();
            return GSON.fromJson(bodyStr, listType);
        }
    }

    public UserProfile syncLearnedWords(String token, int learnedWordsCount, int masteredWordsCount)
            throws IOException {
        JsonObject body = new JsonObject();
        body.addProperty("learnedWordsCount", learnedWordsCount);
        body.addProperty("masteredWordsCount", masteredWordsCount);
        return syncLearningStats(token, body);
    }

    public UserProfile syncLearnedWords(String token, int learnedWordsCount) throws IOException {
        JsonObject body = new JsonObject();
        body.addProperty("learnedWordsCount", learnedWordsCount);
        return syncLearningStats(token, body);
    }

    private UserProfile syncLearningStats(String token, JsonObject body) throws IOException {
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/user/stats/learned-words")
                        .header("Authorization", "Bearer " + token)
                        .put(RequestBody.create(body.toString(), JSON))
                        .build();
        return executeUser(request);
    }

    /** 服务端根据当前登录用户在 MySQL 中的英语水平生成例句 */
    public String aiExample(String token, String word, String phonetic, String translation) throws IOException {
        JsonObject body = new JsonObject();
        body.addProperty("word", word);
        if (phonetic != null) {
            body.addProperty("phonetic", phonetic);
        } else {
            body.addProperty("phonetic", "");
        }
        body.addProperty("translation", translation);
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/ai/example")
                        .header("Authorization", "Bearer " + token)
                        .post(RequestBody.create(body.toString(), JSON))
                        .build();
        return executeContentResponse(request);
    }

    /** 根据今日单词列表与用户在库中的英语水平生成短文 */
    public String aiEssay(String token, List<Word> words) throws IOException {
        JsonArray arr = new JsonArray();
        for (Word w : words) {
            JsonObject o = new JsonObject();
            o.addProperty("word", w.word);
            o.addProperty("translation", w.translation != null ? w.translation : "");
            arr.add(o);
        }
        JsonObject body = new JsonObject();
        body.add("words", arr);
        Request request =
                new Request.Builder()
                        .url(baseUrl + "/api/app/ai/essay")
                        .header("Authorization", "Bearer " + token)
                        .post(RequestBody.create(body.toString(), JSON))
                        .build();
        return executeContentResponse(request);
    }

    private String executeContentResponse(Request request) throws IOException {
        try (Response response = client.newCall(request).execute()) {
            String bodyStr = response.body() != null ? response.body().string() : "";
            if (!response.isSuccessful()) {
                throw new IOException(parseMessage(bodyStr, response.code()));
            }
            JsonObject o = GSON.fromJson(bodyStr, JsonObject.class);
            if (o != null && o.has("content")) {
                return o.get("content").getAsString();
            }
            throw new IOException("响应格式异常");
        }
    }

    private AuthResponse executeAuth(Request request) throws IOException {
        try (Response response = client.newCall(request).execute()) {
            String bodyStr = response.body() != null ? response.body().string() : "";
            if (!response.isSuccessful()) {
                throw new IOException(parseMessage(bodyStr, response.code()));
            }
            return GSON.fromJson(bodyStr, AuthResponse.class);
        }
    }

    private UserProfile executeUser(Request request) throws IOException {
        try (Response response = client.newCall(request).execute()) {
            String bodyStr = response.body() != null ? response.body().string() : "";
            if (!response.isSuccessful()) {
                throw new IOException(parseMessage(bodyStr, response.code()));
            }
            return GSON.fromJson(bodyStr, UserProfile.class);
        }
    }

    private static String parseMessage(String body, int code) {
        try {
            JsonObject o = GSON.fromJson(body, JsonObject.class);
            if (o != null && o.has("message")) {
                return o.get("message").getAsString();
            }
        } catch (Exception ignored) {
        }
        return "请求失败 (" + code + ")";
    }

    public static void syncLearnedWordsCount(android.content.Context context, int learnedWordsCount) {
        SessionManager sm = new SessionManager(context);
        String token = sm.getToken();
        if (token == null) {
            return;
        }
        try {
            UserProfile u = new LebeiApi().syncLearnedWords(token, learnedWordsCount);
            sm.saveProfile(u);
        } catch (IOException ignored) {
        }
    }

    public static void syncLearningStatsCount(
            android.content.Context context, int learnedWordsCount, int masteredWordsCount) {
        SessionManager sm = new SessionManager(context);
        String token = sm.getToken();
        if (token == null) {
            return;
        }
        try {
            UserProfile u = new LebeiApi().syncLearnedWords(token, learnedWordsCount, masteredWordsCount);
            sm.saveProfile(u);
        } catch (IOException ignored) {
        }
    }
}
