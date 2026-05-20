package com.example.lebei;

import android.content.Context;
import android.content.Intent;
import android.media.AudioAttributes;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.speech.tts.TextToSpeech;
import android.speech.tts.TextToSpeech.Engine;
import android.speech.tts.UtteranceProgressListener;
import android.text.Html;
import android.text.Spanned;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import android.util.Log;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentActivity;
import com.example.lebei.api.LebeiApi;
import com.example.lebei.api.UserProfile;
import java.io.IOException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;

public class LearnFragment extends Fragment {

    private static final String TAG = "LearnFragment";

    private TextView tvWord, tvPhonetic, tvTranslation, tvExample, tvEssay, tvSpellingFeedback;
    private Button btnGuide, btnShowExample, btnEasy, btnHard, btnGenerateEssay, btnReadExample, btnReadEssay;
    private EditText etSpellingAnswer;
    private Button btnSubmitSpelling, btnSkipSpelling;
    private Word currentWord;
    private List<Word> todayWords = new ArrayList<>();
    private int currentIndex = 0;
    private ExecutorService executor;
    private AppDatabase db;
    private SessionManager sessionManager;
    private UserProfile currentUser;
    private String currentBookId;
    private int currentDailyReviewLimit;
    private boolean reviewPhaseNoticeShown;
    private int currentDailyNewLimit;
    /** 当日学习计划（含已保存的 AI 例句/短文） */
    private long currentDailyPlanId;
    private List<DailyPlanWord> todayPlanRows = new ArrayList<>();

    private static final String UTTERANCE_ID = "lebei_read";

    private TextToSpeech tts;
    /** onInit 已回调（无论成功失败）；可能来自 binder 线程，与 UI 交互时请回到主线程 */
    private volatile boolean ttsInitFinished;
    private volatile boolean ttsReady;
    /** 引擎尚未就绪时暂存的朗读文本，初始化成功后自动播放 */
    private String pendingSpeakAfterInit;

    private final Handler ttsHandler = new Handler(Looper.getMainLooper());
    private final Runnable ttsBindTimeoutRunnable = this::onTtsBindTimeout;
    /** 用于忽略已 shutdown 的旧引擎的迟到的 onInit */
    private int ttsBindGeneration;
    private int ttsBindAutoRetryCount;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_learn, container, false);

        tvWord = view.findViewById(R.id.tv_word);
        tvPhonetic = view.findViewById(R.id.tv_phonetic);
        tvTranslation = view.findViewById(R.id.tv_translation);
        tvExample = view.findViewById(R.id.tv_example_sentence);
        tvEssay = view.findViewById(R.id.tv_essay_content);
        btnGuide = view.findViewById(R.id.btn_learn_guide);
        btnShowExample = view.findViewById(R.id.btn_show_example);
        btnEasy = view.findViewById(R.id.btn_easy);
        btnHard = view.findViewById(R.id.btn_hard);
        btnGenerateEssay = view.findViewById(R.id.btn_generate_essay);
        btnReadExample = view.findViewById(R.id.btn_read_example);
        btnReadEssay = view.findViewById(R.id.btn_read_essay);
        etSpellingAnswer = view.findViewById(R.id.et_spelling_answer);
        btnSubmitSpelling = view.findViewById(R.id.btn_submit_spelling);
        btnSkipSpelling = view.findViewById(R.id.btn_skip_spelling);
        tvSpellingFeedback = view.findViewById(R.id.tv_spelling_feedback);

        ttsInitFinished = false;
        ttsReady = false;
        pendingSpeakAfterInit = null;
        ttsBindAutoRetryCount = 0;
        // TTS 延迟到用户首次点「朗读」再绑定：避免页面未就绪时绑定失败；并用 Application 上下文（官方推荐）

        executor = Executors.newSingleThreadExecutor();
        db = AppDatabase.getInstance(requireContext());
        sessionManager = new SessionManager(requireContext());

        loadUserAndTodayWords();

        btnGuide.setOnClickListener(
                v ->
                        PageGuideDialog.show(
                                requireContext(), "学习页使用说明", TutorialContent.learnGuide()));
        view.post(
                () -> {
                    if (isAdded()) {
                        PageGuideDialog.showOnce(
                                requireContext(),
                                "learn",
                                "学习页使用说明",
                                TutorialContent.learnGuide());
                    }
                });

        btnShowExample.setOnClickListener(v -> fetchAiExample());
        btnEasy.setOnClickListener(v -> handleAnswer(true));
        btnHard.setOnClickListener(v -> handleAnswer(false));
        btnSubmitSpelling.setOnClickListener(v -> handleSpellingSubmit());
        btnSkipSpelling.setOnClickListener(v -> handleSpellingSkip());
        btnGenerateEssay.setOnClickListener(v -> fetchAiEssay());
        btnReadExample.setOnClickListener(v -> speakPlain(textForSpeech(tvExample.getText().toString())));
        btnReadEssay.setOnClickListener(v -> speakPlain(textForSpeech(tvEssay.getText().toString())));

        return view;
    }

    private void bindSystemTextToSpeech() {
        final int gen = ++ttsBindGeneration;
        Context appCtx = requireContext().getApplicationContext();
        tts =
                new TextToSpeech(
                        appCtx,
                        status -> {
                            if (gen != ttsBindGeneration || tts == null) {
                                return;
                            }
                            ttsHandler.removeCallbacks(ttsBindTimeoutRunnable);
                            handleTtsEngineInit(status);
                        });
    }

    /** 首次点击朗读时再创建引擎，避免 onCreate 阶段 Activity 未稳定导致无声 */
    private void ensureTtsStarted() {
        if (tts != null) {
            return;
        }
        if (!isAdded()) {
            return;
        }
        ttsBindAutoRetryCount = 0;
        bindSystemTextToSpeech();
        scheduleTtsBindTimeout();
    }

    private void scheduleTtsBindTimeout() {
        ttsHandler.removeCallbacks(ttsBindTimeoutRunnable);
        ttsHandler.postDelayed(ttsBindTimeoutRunnable, 3500);
    }

    /** 长时间无 onInit 时重建引擎（仅自动重试 1 次，避免死循环） */
    private void onTtsBindTimeout() {
        if (ttsInitFinished || !isAdded()) {
            return;
        }
        if (ttsBindAutoRetryCount >= 1) {
            postTtsToast("语音引擎无法连接，请到系统设置 → 文字转语音 检查默认引擎与英语语音包。");
            return;
        }
        ttsBindAutoRetryCount++;
        String queued = pendingSpeakAfterInit;
        ttsBindGeneration++;
        if (tts != null) {
            try {
                tts.stop();
                tts.shutdown();
            } catch (Exception ignored) {
            }
            tts = null;
        }
        ttsInitFinished = false;
        ttsReady = false;
        pendingSpeakAfterInit = queued;
        bindSystemTextToSpeech();
        scheduleTtsBindTimeout();
        postTtsToast("语音引擎启动偏慢，已重新连接，请再点一次「朗读」或稍候。");
    }

    private void handleTtsEngineInit(int status) {
        if (tts == null) {
            return;
        }
        if (status == TextToSpeech.SUCCESS) {
            // USAGE_MEDIA：走「媒体」音量，避免无障碍声道被关成 0 导致完全无声（小米/华为等常见）
            tts.setAudioAttributes(
                    new AudioAttributes.Builder()
                            .setUsage(AudioAttributes.USAGE_MEDIA)
                            .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                            .build());
            tts.setSpeechRate(1.0f);
            tts.setPitch(1.0f);
            int r = tts.setLanguage(Locale.forLanguageTag("en-US"));
            if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
                r = tts.setLanguage(Locale.US);
            }
            if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
                r = tts.setLanguage(Locale.UK);
            }
            if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
                r = tts.setLanguage(Locale.ENGLISH);
            }
            if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
                r = tts.setLanguage(Locale.CHINESE);
            }
            // 引擎已连上即允许朗读：LANG_MISSING_DATA 仍可能走在线合成；若真无声用户可按提示装语音包
            ttsReady = true;
            tts.setOnUtteranceProgressListener(
                    new UtteranceProgressListener() {
                        @Override
                        public void onStart(String utteranceId) {}

                        @Override
                        public void onDone(String utteranceId) {}

                        @Override
                        public void onError(String utteranceId) {
                            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) {
                                postTtsToast("朗读失败，请检查系统文字转语音设置或重试。");
                            }
                        }

                        @Override
                        public void onError(String utteranceId, int errorCode) {
                            postTtsToast("朗读失败，请检查系统文字转语音设置或重试。");
                        }
                    });
        } else {
            ttsReady = false;
            postTtsToast("语音引擎连接失败，请到系统设置 → 文字转语音 选择引擎并下载语音包。");
        }
        ttsInitFinished = true;
        scheduleAfterTtsInit();
    }

    private void tryOpenTtsInstaller() {
        try {
            startActivity(new Intent(Engine.ACTION_INSTALL_TTS_DATA));
        } catch (Exception ignored) {
        }
    }

    private void scheduleAfterTtsInit() {
        Runnable drain =
                () -> {
                    if (tts == null || !isAdded() || getContext() == null) {
                        return;
                    }
                    if (!ttsReady) {
                        Toast.makeText(
                                        getContext(),
                                        "语音引擎不可用。已尝试打开系统语音包安装页，也可在设置中搜索「文字转语音」。",
                                        Toast.LENGTH_LONG)
                                .show();
                        pendingSpeakAfterInit = null;
                        return;
                    }
                    String pending = pendingSpeakAfterInit;
                    pendingSpeakAfterInit = null;
                    if (pending != null && !pending.trim().isEmpty()) {
                        doSpeak(pending);
                    }
                };
        if (Looper.myLooper() == Looper.getMainLooper()) {
            drain.run();
        } else {
            FragmentActivity act = getActivity();
            if (act != null) {
                act.runOnUiThread(drain);
            } else {
                new Handler(Looper.getMainLooper()).post(drain);
            }
        }
    }

    private void postTtsToast(String msg) {
        FragmentActivity act = getActivity();
        if (act == null) {
            return;
        }
        act.runOnUiThread(
                () -> {
                    if (isAdded() && getContext() != null) {
                        Toast.makeText(getContext(), msg, Toast.LENGTH_SHORT).show();
                    }
                });
    }

    /** 走英文 TTS：截掉「中文大意」段并去掉汉字，避免部分引擎对中英混排长文无声 */
    private static String prepareEnglishTtsText(String text) {
        if (text == null) {
            return "";
        }
        String s = text;
        int zhIdx = s.indexOf("中文大意");
        if (zhIdx >= 0) {
            s = s.substring(0, zhIdx);
        }
        s = s.replaceAll("[\\u4e00-\\u9fff\\uff00-\\uffef]+", " ");
        s = s.replaceAll("\\s+", " ").trim();
        return s;
    }

    /** prepareEnglishTtsText 为空时：至少去掉「中文大意」后文，保留中英混排交给系统引擎 */
    private static String fallbackSpeakableForTts(String text) {
        if (text == null) {
            return "";
        }
        int i = text.indexOf("中文大意");
        String s = i >= 0 ? text.substring(0, i) : text;
        return s.replaceAll("\\s+", " ").trim();
    }

    private void speakPlain(String text) {
        if (text == null || text.trim().isEmpty()) {
            Toast.makeText(getContext(), "暂无可朗读内容", Toast.LENGTH_SHORT).show();
            return;
        }
        ensureTtsStarted();
        if (tts == null) {
            Toast.makeText(getContext(), "语音引擎未就绪", Toast.LENGTH_SHORT).show();
            return;
        }
        if (!ttsInitFinished) {
            pendingSpeakAfterInit = text;
            Toast.makeText(getContext(), "正在连接系统语音引擎…", Toast.LENGTH_SHORT).show();
            return;
        }
        if (!ttsReady) {
            Toast.makeText(getContext(), "语音引擎不可用", Toast.LENGTH_SHORT).show();
            tryOpenTtsInstaller();
            return;
        }
        doSpeak(text);
    }

    private void doSpeak(String text) {
        String toSpeak = prepareEnglishTtsText(text);
        if (toSpeak.isEmpty()) {
            toSpeak = fallbackSpeakableForTts(text);
        }
        if (toSpeak.isEmpty()) {
            Toast.makeText(requireContext(), "暂无可朗读内容", Toast.LENGTH_SHORT).show();
            return;
        }
        tts.stop();
        Bundle params = new Bundle();
        params.putString(TextToSpeech.Engine.KEY_PARAM_UTTERANCE_ID, UTTERANCE_ID);
        int code = tts.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, params, UTTERANCE_ID);
        if (code == TextToSpeech.ERROR) {
            Toast.makeText(requireContext(), "朗读未能启动，请尝试安装系统语音包。", Toast.LENGTH_SHORT).show();
            tryOpenTtsInstaller();
        }
    }

    private static String stripAiPrefix(String raw) {
        if (raw == null) {
            return "";
        }
        return raw.replaceFirst("^💡\\s*AI例句:\\s*", "").replaceFirst("^\\s+", "").trim();
    }

    /** 去掉 UI 占位/提示文案，避免朗读「正在生成」等或空串 */
    private static String textForSpeech(String raw) {
        String s = stripAiPrefix(raw);
        if (s.contains("正在生成短文") || s.contains("生成失败")) {
            return "";
        }
        return s;
    }

    @Override
    public void onResume() {
        super.onResume();
        if (executor == null || executor.isShutdown()) {
            return;
        }
        executor.execute(
                () -> {
                    UserProfile u = sessionManager.getProfile();
                    if (u != null && currentBookId != null) {
                        String book = u.currentBookId != null ? u.currentBookId : "CET4";
                        int dailyReview = Math.max(0, Math.min(u.dailyReviewWords, 500));
                        int dailyNew = Math.max(0, Math.min(u.dailyNewWords, 200));
                        if (!Objects.equals(book, currentBookId)
                                || dailyReview != currentDailyReviewLimit
                                || dailyNew != currentDailyNewLimit) {
                            FragmentActivity a = getActivity();
                            if (a != null && isAdded()) {
                                a.runOnUiThread(
                                        () -> {
                                            if (!isAdded()) {
                                                return;
                                            }
                                            todayWords.clear();
                                            todayPlanRows.clear();
                                            currentDailyPlanId = 0;
                                            currentIndex = 0;
                                            loadUserAndTodayWords();
                                        });
                            }
                        }
                    }
                });
    }

    /**
     * 用户所选 bookId 在本地无词时，按固定顺序择一有词条的词库，用于抽取「新词」，避免当日计划为空。
     */
    private static String pickLocalBookForNewWords(WordDao dao, String profileBookId) {
        String p =
                profileBookId != null && !profileBookId.trim().isEmpty()
                        ? profileBookId.trim()
                        : "CET4";
        List<String> candidates = new ArrayList<>();
        candidates.add(p);
        String[] order = {"CET4", "CET6", "IELTS", "TOEFL", "JUNIOR_HIGH", "SENIOR_HIGH"};
        for (String b : order) {
            if (!candidates.contains(b)) {
                candidates.add(b);
            }
        }
        for (String b : candidates) {
            List<Integer> x = dao.getWordIdsInBook(b);
            if (x != null && !x.isEmpty()) {
                return b;
            }
        }
        return p;
    }

    private void loadUserAndTodayWords() {
        if (executor == null || executor.isShutdown()) {
            return;
        }
        try {
            executor.execute(
                    () -> {
                    if (sessionManager.getToken() == null) {
                        FragmentActivity act0 = getActivity();
                        if (act0 != null) {
                            act0.runOnUiThread(
                                    () -> {
                                        if (!isAdded() || getContext() == null) {
                                            return;
                                        }
                                        Toast.makeText(getContext(), "请重新登录", Toast.LENGTH_SHORT).show();
                                        act0.finish();
                                    });
                        }
                        return;
                    }
                    UserProfile u = sessionManager.getProfile();
                    if (u == null) {
                        try {
                            u = new LebeiApi().getMe(sessionManager.getToken());
                            if (u != null) {
                                sessionManager.saveProfile(u);
                            }
                        } catch (IOException e) {
                            FragmentActivity actE = getActivity();
                            if (actE != null) {
                                actE.runOnUiThread(
                                        () -> {
                                            if (!isAdded() || getContext() == null) {
                                                return;
                                            }
                                            Toast.makeText(
                                                            getContext(),
                                                            e.getMessage() != null ? e.getMessage() : "加载失败",
                                                            Toast.LENGTH_SHORT)
                                                    .show();
                                        });
                            }
                            return;
                        }
                    }
                    if (u == null) {
                        FragmentActivity actNull = getActivity();
                        if (actNull != null) {
                            actNull.runOnUiThread(
                                    () -> {
                                        if (!isAdded() || getContext() == null) {
                                            return;
                                        }
                                        Toast.makeText(
                                                        getContext(),
                                                        "用户信息为空，请重新登录",
                                                        Toast.LENGTH_LONG)
                                                .show();
                                        applyEmptyLearnStateOnUi();
                                    });
                        }
                        return;
                    }
                    currentUser = u;
                    currentBookId = u.currentBookId != null ? u.currentBookId : "CET4";
                    final UserProfile planUser = u;
                    final int safeDailyReview =
                            Math.max(0, Math.min(planUser.dailyReviewWords, 500));
                    final int safeDailyNew = Math.max(0, Math.min(planUser.dailyNewWords, 200));
                    currentDailyReviewLimit = safeDailyReview;
                    currentDailyNewLimit = safeDailyNew;

                    final String[] savedEssayHolder = new String[1];
                    final int[] firstUnlearnedHolder = new int[1];
                    final boolean[] bookFallbackHint = new boolean[1];
                    final Context appCtx =
                            getContext() != null ? getContext().getApplicationContext() : null;
                    if (appCtx == null) {
                        return;
                    }
                    try {
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                DataProvider.ensureVocabularyFromAssets(appCtx, db);

                                String dateKey = LocalDate.now().toString();
                                String yesterdayKey = LocalDate.now().minusDays(1).toString();
                                DailyPlanDao planDao = db.dailyPlanDao();

                                final String bookForNewWordPool =
                                        pickLocalBookForNewWords(db.wordDao(), currentBookId);
                                bookFallbackHint[0] =
                                        !bookForNewWordPool.equals(currentBookId);

                                DailyPlan existing = planDao.getPlanByDateAndBook(dateKey, currentBookId);
                                long planId;
                                List<DailyPlanWord> rows;
                                if (existing != null) {
                                    planId = existing.id;
                                    List<DailyPlanWord> rawRows = planDao.getPlanWords(planId);
                                    rows =
                                            rawRows != null
                                                    ? new ArrayList<>(rawRows)
                                                    : new ArrayList<>();
                                    long now = System.currentTimeMillis();
                                    db.wordDao().decayMasteredWords(now);
                                    List<Word> dueReviewWords =
                                            db.wordDao().getWordsForReview(now, safeDailyReview);
                                    rows =
                                            refreshExistingPlanDueReviews(
                                                    planDao, planId, rows, dueReviewWords);
                                } else {
                                    long now = System.currentTimeMillis();
                                    db.wordDao().decayMasteredWords(now);
                                    List<Word> reviewWords =
                                            db.wordDao().getWordsForReview(now, safeDailyReview);
                                    Set<Integer> used = new HashSet<>();
                                    List<Integer> reviewIds = new ArrayList<>();
                                    if (reviewWords != null) {
                                        for (Word w : reviewWords) {
                                            if (w != null && !used.contains(w.id)) {
                                                reviewIds.add(w.id);
                                                used.add(w.id);
                                            }
                                        }
                                    }
                                    List<Integer> newIds =
                                            DailyWordPicker.pickNewWordIds(
                                                    db.wordDao(),
                                                    planDao,
                                                    dateKey,
                                                    bookForNewWordPool,
                                                    safeDailyNew,
                                                    yesterdayKey,
                                                    used);
                                    List<Integer> orderedIds =
                                            DailyReviewPlanPolicy.newThenReviewIds(reviewIds, newIds);

                                    if (orderedIds.isEmpty()) {
                                        planId = 0;
                                        rows = new ArrayList<>();
                                    } else {
                                        DailyPlan plan =
                                                new DailyPlan(dateKey, currentBookId, orderedIds.size());
                                        List<DailyPlanWord> toInsert = new ArrayList<>();
                                        for (int i = 0; i < orderedIds.size(); i++) {
                                            toInsert.add(new DailyPlanWord(0, orderedIds.get(i), i));
                                        }
                                        planId = planDao.insertPlanWithWords(plan, toInsert);
                                        List<DailyPlanWord> insertedRows = planDao.getPlanWords(planId);
                                        rows =
                                                insertedRows != null
                                                        ? new ArrayList<>(insertedRows)
                                                        : new ArrayList<>();
                                    }
                                }

                                List<Word> ordered = loadOrderedWordsForRows(rows);
                                if (ordered.isEmpty() && planId > 0) {
                                    planDao.deletePlanById(planId);
                                    planId = 0;
                                    rows = new ArrayList<>();
                                }
                                todayPlanRows = rows;
                                todayWords = ordered;
                                currentDailyPlanId = planId;

                                DailyPlan planRow = planId > 0 ? planDao.getPlanById(planId) : null;
                                savedEssayHolder[0] =
                                        planRow != null && planRow.essayText != null
                                                ? planRow.essayText
                                                : "";
                                firstUnlearnedHolder[0] = findFirstUnlearnedIndex();
                            });
                    } catch (RuntimeException e) {
                        Log.e(TAG, "loadUserAndTodayWords db/plan", e);
                        FragmentActivity actEx = getActivity();
                        if (actEx != null) {
                            actEx.runOnUiThread(
                                    () -> {
                                        if (!isAdded() || getContext() == null) {
                                            return;
                                        }
                                        String hint =
                                                e.getMessage() != null && e.getMessage().length() < 80
                                                        ? e.getMessage()
                                                        : "加载学习数据失败，请稍后重试或重新登录";
                                        Toast.makeText(getContext(), hint, Toast.LENGTH_LONG).show();
                                        applyEmptyLearnStateOnUi();
                                    });
                        }
                        return;
                    }
                    final String savedEssay =
                            savedEssayHolder[0] != null ? savedEssayHolder[0] : "";
                    final int firstUnlearned = firstUnlearnedHolder[0];

                    FragmentActivity act = getActivity();
                    if (act == null || !isAdded()) {
                        return;
                    }
                    act.runOnUiThread(
                            () -> {
                                if (!isAdded() || getContext() == null || getView() == null) {
                                    return;
                                }
                                if (todayWords.isEmpty()) {
                                    Toast.makeText(
                                                    getContext(),
                                                    "当前词库暂无可用单词（请检查计划中的每日新词/复习量或词库）。",
                                                    Toast.LENGTH_LONG)
                                            .show();
                                    applyEmptyLearnStateOnUi();
                                } else {
                                    btnEasy.setEnabled(true);
                                    btnHard.setEnabled(true);
                                    btnShowExample.setEnabled(true);
                                    if (bookFallbackHint[0]) {
                                        Toast.makeText(
                                                        getContext(),
                                                        "所选词库在本地词条较少，已用其它内置词库补足今日新词。",
                                                        Toast.LENGTH_LONG)
                                                .show();
                                    }
                                    showSpellingFeedback(null);
                                    if (!savedEssay.isEmpty()) {
                                        setEssayText(savedEssay);
                                        btnReadEssay.setVisibility(View.VISIBLE);
                                    } else {
                                        tvEssay.setText("");
                                        btnReadEssay.setVisibility(View.GONE);
                                    }
                                    if (firstUnlearned == LearnProgressPolicy.NO_NEXT_INDEX) {
                                        applyCompletedLearnStateOnUi("今日计划中的单词已全部学完，可生成复习短文。");
                                    } else {
                                        currentIndex = firstUnlearned;
                                        showWord(currentIndex);
                                    }
                                }
                            });
                    });
        } catch (RejectedExecutionException e) {
            Log.w(TAG, "loadUserAndTodayWords rejected", e);
        }
    }

    private int findFirstUnlearnedIndex() {
        List<Integer> learnedFlags = new ArrayList<>(todayPlanRows.size());
        for (DailyPlanWord row : todayPlanRows) {
            learnedFlags.add(row != null ? row.learned : 0);
        }
        int wordCount = todayWords != null ? todayWords.size() : 0;
        return LearnProgressPolicy.firstUnlearnedIndex(learnedFlags, wordCount);
    }

    private List<Word> loadOrderedWordsForRows(List<DailyPlanWord> rows) {
        List<Integer> wordIds = new ArrayList<>();
        if (rows != null) {
            for (DailyPlanWord r : rows) {
                if (r != null) {
                    wordIds.add(r.wordId);
                }
            }
        }
        List<Word> loaded = db.wordDao().getWordsByIdsChunked(wordIds);
        Map<Integer, Word> byId = new HashMap<>();
        if (loaded != null) {
            for (Word w : loaded) {
                byId.put(w.id, w);
            }
        }
        List<Word> ordered = new ArrayList<>();
        if (rows != null) {
            for (DailyPlanWord r : rows) {
                if (r == null) {
                    continue;
                }
                Word w = byId.get(r.wordId);
                if (w != null) {
                    ordered.add(w);
                }
            }
        }
        return ordered;
    }

    private List<DailyPlanWord> refreshExistingPlanDueReviews(
            DailyPlanDao planDao, long planId, List<DailyPlanWord> rows, List<Word> dueReviewWords) {
        if (planId <= 0 || dueReviewWords == null || dueReviewWords.isEmpty()) {
            return rows;
        }
        List<Integer> existingIds = new ArrayList<>();
        List<Integer> learnedFlags = new ArrayList<>();
        for (DailyPlanWord row : rows) {
            if (row != null) {
                existingIds.add(row.wordId);
                learnedFlags.add(row.learned);
            }
        }
        List<Integer> dueIds = new ArrayList<>();
        for (Word word : dueReviewWords) {
            if (word != null) {
                dueIds.add(word.id);
            }
        }

        List<Integer> reopenIds =
                DailyReviewPlanPolicy.dueIdsToReopen(existingIds, learnedFlags, dueIds);
        if (!reopenIds.isEmpty()) {
            planDao.markUnlearned(planId, reopenIds);
            Set<Integer> reopenSet = new HashSet<>(reopenIds);
            for (DailyPlanWord row : rows) {
                if (row != null && reopenSet.contains(row.wordId)) {
                    row.learned = 0;
                }
            }
        }

        List<Integer> appendIds = DailyReviewPlanPolicy.dueIdsToAppend(existingIds, dueIds);
        if (!appendIds.isEmpty()) {
            int nextSort = 0;
            for (DailyPlanWord row : rows) {
                if (row != null && row.sortOrder >= nextSort) {
                    nextSort = row.sortOrder + 1;
                }
            }
            List<DailyPlanWord> toInsert = new ArrayList<>();
            for (Integer wordId : appendIds) {
                if (wordId != null) {
                    toInsert.add(new DailyPlanWord(planId, wordId, nextSort++));
                }
            }
            if (!toInsert.isEmpty()) {
                planDao.insertPlanWords(toInsert);
                List<DailyPlanWord> refreshedRows = planDao.getPlanWords(planId);
                rows =
                        refreshedRows != null
                                ? new ArrayList<>(refreshedRows)
                                : rows;
                planDao.updateTargetCount(planId, rows.size());
            }
        }
        rows = reorderExistingPlanDueReviews(planDao, planId, rows, dueIds);
        return rows;
    }

    private List<DailyPlanWord> reorderExistingPlanDueReviews(
            DailyPlanDao planDao, long planId, List<DailyPlanWord> rows, List<Integer> dueIds) {
        if (rows == null || rows.isEmpty() || dueIds == null || dueIds.isEmpty()) {
            return rows;
        }
        List<Integer> existingIds = new ArrayList<>();
        List<Integer> learnedFlags = new ArrayList<>();
        for (DailyPlanWord row : rows) {
            if (row != null) {
                existingIds.add(row.wordId);
                learnedFlags.add(row.learned);
            }
        }
        List<Integer> orderedIds =
                DailyReviewPlanPolicy.reorderExistingPlanIdsForDueReviews(
                        existingIds, learnedFlags, dueIds);
        if (orderedIds.isEmpty() || orderedIds.equals(existingIds)) {
            return rows;
        }
        planDao.updateSortOrders(planId, orderedIds);
        List<DailyPlanWord> refreshedRows = planDao.getPlanWords(planId);
        return refreshedRows != null ? new ArrayList<>(refreshedRows) : rows;
    }

    private void refreshDueReviewsForCurrentPlanLocked(long now) {
        if (currentDailyPlanId <= 0 || currentDailyReviewLimit <= 0) {
            return;
        }
        db.wordDao().decayMasteredWords(now);
        List<Word> dueReviewWords = db.wordDao().getWordsForReview(now, currentDailyReviewLimit);
        todayPlanRows =
                refreshExistingPlanDueReviews(
                        db.dailyPlanDao(), currentDailyPlanId, todayPlanRows, dueReviewWords);
        todayWords = loadOrderedWordsForRows(todayPlanRows);
    }

    /** 后台线程回到 UI 时调用，避免 Fragment 已销毁仍执行 requireActivity() 崩溃 */
    private void postToUi(Runnable r) {
        FragmentActivity a = getActivity();
        if (a == null || !isAdded()) {
            return;
        }
        a.runOnUiThread(
                () -> {
                    if (!isAdded() || getView() == null) {
                        return;
                    }
                    r.run();
                });
    }

    /** 无当日学习任务时清空界面，避免沿用旧单词触发异常 */
    private void applyEmptyLearnStateOnUi() {
        currentWord = null;
        currentIndex = 0;
        tvWord.setText("暂无可学单词");
        tvPhonetic.setText("");
        tvTranslation.setText(
                "若刚安装请稍候；否则请到「计划」调高每日新词或复习量，或切换词库后再试。");
        tvExample.setVisibility(View.GONE);
        tvExample.setText("");
        btnReadExample.setVisibility(View.GONE);
        etSpellingAnswer.setText("");
        etSpellingAnswer.setVisibility(View.GONE);
        btnSubmitSpelling.setVisibility(View.GONE);
        btnSkipSpelling.setVisibility(View.GONE);
        showSpellingFeedback(null);
        tvEssay.setText("");
        btnReadEssay.setVisibility(View.GONE);
        btnEasy.setEnabled(false);
        btnHard.setEnabled(false);
        btnShowExample.setEnabled(false);
    }

    private void applyCompletedLearnStateOnUi(@Nullable String feedback) {
        currentWord = null;
        tvWord.setText("今日计划已完成");
        tvPhonetic.setText("");
        tvTranslation.setText("可生成复习短文，或明天继续复习。");
        tvExample.setVisibility(View.GONE);
        tvExample.setText("");
        btnReadExample.setVisibility(View.GONE);
        etSpellingAnswer.setText("");
        etSpellingAnswer.setVisibility(View.GONE);
        btnSubmitSpelling.setVisibility(View.GONE);
        btnSkipSpelling.setVisibility(View.GONE);
        btnEasy.setVisibility(View.GONE);
        btnHard.setVisibility(View.GONE);
        btnEasy.setEnabled(false);
        btnHard.setEnabled(false);
        btnShowExample.setEnabled(false);
        showSpellingFeedback(feedback);
    }

    private void showSpellingFeedback(@Nullable String message) {
        if (tvSpellingFeedback == null) {
            return;
        }
        if (message == null || message.trim().isEmpty()) {
            tvSpellingFeedback.setText("");
            tvSpellingFeedback.setVisibility(View.GONE);
            return;
        }
        tvSpellingFeedback.setText(message.trim());
        tvSpellingFeedback.setVisibility(View.VISIBLE);
    }

    private void setEssayText(String markdown) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            Spanned rendered =
                    Html.fromHtml(MarkdownText.toHtml(markdown), Html.FROM_HTML_MODE_LEGACY);
            tvEssay.setText(rendered);
        } else {
            tvEssay.setText(Html.fromHtml(MarkdownText.toHtml(markdown)));
        }
    }

    private DailyPlanWord rowForCurrentWord() {
        if (currentWord == null) {
            return null;
        }
        for (DailyPlanWord r : todayPlanRows) {
            if (r.wordId == currentWord.id) {
                return r;
            }
        }
        return null;
    }

    private void maybeShowReviewPhaseNotice(boolean reviewMode) {
        if (!reviewMode || reviewPhaseNoticeShown || !isAdded() || getContext() == null) {
            return;
        }
        reviewPhaseNoticeShown = true;
        new androidx.appcompat.app.AlertDialog.Builder(requireContext())
                .setTitle("进入复习环节")
                .setMessage("今日新词已经学完，接下来会复习到期单词。请根据中文释义输入英文拼写。")
                .setPositiveButton("开始复习", null)
                .show();
    }

    private void showWord(int index) {
        if (todayWords != null && index < todayWords.size()) {
            currentWord = todayWords.get(index);
            boolean reviewMode = currentWord.familiarity > 0;
            maybeShowReviewPhaseNotice(reviewMode);
            tvWord.setText(reviewMode ? "请拼写单词" : currentWord.word);
            tvPhonetic.setText(currentWord.phonetic);
            tvTranslation.setText(currentWord.translation);
            etSpellingAnswer.setText("");
            etSpellingAnswer.setVisibility(reviewMode ? View.VISIBLE : View.GONE);
            btnSubmitSpelling.setVisibility(reviewMode ? View.VISIBLE : View.GONE);
            btnSkipSpelling.setVisibility(reviewMode ? View.VISIBLE : View.GONE);
            btnEasy.setVisibility(reviewMode ? View.GONE : View.VISIBLE);
            btnHard.setVisibility(reviewMode ? View.GONE : View.VISIBLE);
            btnShowExample.setEnabled(!reviewMode);
            if (!reviewMode) {
                showSpellingFeedback(null);
            }

            DailyPlanWord row = rowForCurrentWord();
            if (!reviewMode
                    && row != null
                    && row.aiExampleText != null
                    && !row.aiExampleText.trim().isEmpty()) {
                tvExample.setText("💡 AI例句:\n" + row.aiExampleText.trim());
                tvExample.setVisibility(View.VISIBLE);
                btnReadExample.setVisibility(View.VISIBLE);
            } else {
                tvExample.setVisibility(View.GONE);
                tvExample.setText("");
                btnReadExample.setVisibility(View.GONE);
            }
        }
    }

    private void fetchAiExample() {
        if (currentWord == null) {
            return;
        }
        String token = sessionManager.getToken();
        if (token == null) {
            return;
        }
        btnShowExample.setEnabled(false);
        executor.execute(
                () -> {
                    try {
                        String content =
                                new LebeiApi()
                                        .aiExample(
                                                token,
                                                currentWord.word,
                                                currentWord.phonetic != null ? currentWord.phonetic : "",
                                                currentWord.translation != null ? currentWord.translation : "");
                        String stored = stripAiPrefix(content).trim();
                        LocalLearningDataStore.withDbLock(
                                () -> {
                                    if (currentDailyPlanId > 0) {
                                        db.dailyPlanDao()
                                                .updateExample(
                                                        currentDailyPlanId, currentWord.id, stored);
                                        for (DailyPlanWord r : todayPlanRows) {
                                            if (r.wordId == currentWord.id) {
                                                r.aiExampleText = stored;
                                                break;
                                            }
                                        }
                                    }
                                });
                        postToUi(
                                () -> {
                                    tvExample.setText("💡 AI例句:\n" + content);
                                    tvExample.setVisibility(View.VISIBLE);
                                    btnReadExample.setVisibility(View.VISIBLE);
                                });
                    } catch (IOException e) {
                        postToUi(
                                () ->
                                        Toast.makeText(
                                                        getContext(),
                                                        e.getMessage() != null ? e.getMessage() : "生成失败",
                                                        Toast.LENGTH_LONG)
                                                .show());
                    } finally {
                        postToUi(() -> btnShowExample.setEnabled(true));
                    }
                });
    }

    private void fetchAiEssay() {
        String token = sessionManager.getToken();
        if (token == null) {
            return;
        }
        btnGenerateEssay.setEnabled(false);
        tvEssay.setText("正在生成短文，请稍候…");
        executor.execute(
                () -> {
                    final ArrayList<Word> learnedToday = new ArrayList<>();
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                Map<Integer, Word> byId = new HashMap<>();
                                List<Integer> learnedIds = new ArrayList<>();
                                for (DailyPlanWord r : todayPlanRows) {
                                    if (r.learned != 0) {
                                        learnedIds.add(r.wordId);
                                    }
                                }
                                if (!learnedIds.isEmpty()) {
                                    List<Word> loaded = db.wordDao().getWordsByIdsChunked(learnedIds);
                                    if (loaded != null) {
                                        for (Word w : loaded) {
                                            byId.put(w.id, w);
                                        }
                                    }
                                    for (DailyPlanWord r : todayPlanRows) {
                                        if (r.learned != 0) {
                                            Word w = byId.get(r.wordId);
                                            if (w != null) {
                                                learnedToday.add(w);
                                            }
                                        }
                                    }
                                }
                            });
                    if (learnedToday.isEmpty()) {
                        postToUi(
                                () -> {
                                    tvEssay.setText(
                                            "请先在上方单词学习界面，对至少一个单词点击「简单」或「困难」后再生成短文。");
                                    btnReadEssay.setVisibility(View.GONE);
                                    btnGenerateEssay.setEnabled(true);
                                });
                        return;
                    }
                    try {
                        String content = new LebeiApi().aiEssay(token, learnedToday);
                        String trimmed = content != null ? content.trim() : "";
                        if (currentDailyPlanId > 0 && !trimmed.isEmpty()) {
                            LocalLearningDataStore.withDbLock(
                                    () ->
                                            db.dailyPlanDao()
                                                    .updateEssay(currentDailyPlanId, trimmed));
                        }
                        postToUi(
                                () -> {
                                    setEssayText(content);
                                    btnReadEssay.setVisibility(View.VISIBLE);
                                });
                    } catch (IOException e) {
                        postToUi(
                                () -> {
                                    tvEssay.setText("生成失败，请检查网络或稍后重试。");
                                    Toast.makeText(
                                                    getContext(),
                                                    e.getMessage() != null ? e.getMessage() : "生成失败",
                                                    Toast.LENGTH_LONG)
                                            .show();
                                    btnReadEssay.setVisibility(View.GONE);
                                });
                    } finally {
                        postToUi(() -> btnGenerateEssay.setEnabled(true));
                    }
                });
    }

    private void handleAnswer(boolean isEasy) {
        if (currentWord == null) {
            return;
        }
        Word answeredWord = currentWord;
        boolean newWord = answeredWord.familiarity <= 0;
        persistAnsweredWord(answeredWord, isEasy, newWord, null);
    }

    private void handleSpellingSubmit() {
        if (currentWord == null) {
            return;
        }
        String answer = etSpellingAnswer.getText().toString();
        if (WordReviewPolicy.normalizeSpelling(answer).isEmpty()) {
            Toast.makeText(getContext(), "请输入单词拼写", Toast.LENGTH_SHORT).show();
            return;
        }
        Word answeredWord = currentWord;
        boolean correct = WordReviewPolicy.spellingsMatch(answeredWord.word, answer);
        String msg =
                correct
                        ? "拼写正确，已进入下一词。"
                        : "拼写错误，正确拼写：" + answeredWord.word + "，已进入下一词。";
        persistAnsweredWord(answeredWord, correct, false, msg);
    }

    private void handleSpellingSkip() {
        if (currentWord == null || currentWord.familiarity <= 0) {
            return;
        }
        Word skippedWord = currentWord;
        String msg = "已跳过，正确拼写：" + skippedWord.word + "。";
        executor.execute(
                () -> {
                    Context appCtx =
                            getContext() != null ? getContext().getApplicationContext() : null;
                    long now = System.currentTimeMillis();
                    int nextWeight =
                            WordReviewPolicy.weightAfterSpellingResult(skippedWord.familiarity, false);
                    skippedWord.familiarity = nextWeight;
                    skippedWord.nextReviewTime =
                            WordReviewPolicy.nextReviewTime(now, nextWeight, false);
                    skippedWord.reviewCount++;
                    final int[] learnedHolder = new int[1];
                    final int[] masteredHolder = new int[1];
                    final int[] nextHolder = new int[] {LearnProgressPolicy.NO_NEXT_INDEX};
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                db.wordDao().update(skippedWord);
                                markPlanWordLearned(skippedWord.id);
                                refreshDueReviewsForCurrentPlanLocked(now);
                                learnedHolder[0] = db.wordDao().getLearnedWordsCount();
                                masteredHolder[0] = db.wordDao().getMasteredWordsCount();
                                nextHolder[0] = findFirstUnlearnedIndex();
                            });
                    if (appCtx != null) {
                        LebeiApi.syncLearningStatsCount(appCtx, learnedHolder[0], masteredHolder[0]);
                    }
                    postToUi(() -> showResultAndAdvance(nextHolder[0], msg));
                });
    }

    private void persistAnsweredWord(
            Word answeredWord, boolean correct, boolean newWord, @Nullable String resultMessage) {
        final String token = sessionManager.getToken();
        if (token == null) {
            return;
        }
        executor.execute(
                () -> {
                    Context appCtx =
                            getContext() != null ? getContext().getApplicationContext() : null;
                    if (appCtx == null) {
                        return;
                    }
                    long now = System.currentTimeMillis();
                    int nextWeight =
                            newWord
                                    ? WordReviewPolicy.weightAfterNewWord(correct)
                                    : WordReviewPolicy.weightAfterSpellingResult(
                                            answeredWord.familiarity, correct);
                    answeredWord.familiarity = nextWeight;
                    answeredWord.nextReviewTime =
                            newWord
                                    ? WordReviewPolicy.firstSameDayReviewTime(now)
                                    : WordReviewPolicy.nextReviewTime(now, nextWeight, correct);
                    answeredWord.reviewCount++;
                    final int[] learnedHolder = new int[1];
                    final int[] masteredHolder = new int[1];
                    final int[] nextHolder = new int[] {LearnProgressPolicy.NO_NEXT_INDEX};
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                db.wordDao().update(answeredWord);
                                markPlanWordLearned(answeredWord.id);
                                refreshDueReviewsForCurrentPlanLocked(now);
                                learnedHolder[0] = db.wordDao().getLearnedWordsCount();
                                masteredHolder[0] = db.wordDao().getMasteredWordsCount();
                                nextHolder[0] = findFirstUnlearnedIndex();
                            });

                    LebeiApi.syncLearningStatsCount(appCtx, learnedHolder[0], masteredHolder[0]);
                    try {
                        UserProfile updated = new LebeiApi().recordStudyWord(token);
                        sessionManager.saveProfile(updated);
                    } catch (IOException ignored) {
                    }

                    postToUi(() -> showResultAndAdvance(nextHolder[0], resultMessage));
                });
    }

    private void markPlanWordLearned(int wordId) {
        if (currentDailyPlanId <= 0) {
            return;
        }
        db.dailyPlanDao().markLearned(currentDailyPlanId, wordId);
        for (DailyPlanWord r : todayPlanRows) {
            if (r.wordId == wordId) {
                r.learned = 1;
                break;
            }
        }
    }

    private void showResultAndAdvance(int nextIndex, @Nullable String resultMessage) {
        if (nextIndex == LearnProgressPolicy.NO_NEXT_INDEX) {
            String feedback =
                    resultMessage != null && !resultMessage.trim().isEmpty()
                            ? resultMessage + "\n太棒了！今日计划中的单词已全部完成。"
                            : "太棒了！今日计划中的单词已全部完成。";
            applyCompletedLearnStateOnUi(feedback);
            return;
        }
        currentIndex = nextIndex;
        showWord(currentIndex);
        showSpellingFeedback(resultMessage);
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        ttsHandler.removeCallbacks(ttsBindTimeoutRunnable);
        ttsBindGeneration++;
        pendingSpeakAfterInit = null;
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
        ttsInitFinished = false;
        ttsReady = false;
        executor.shutdown();
    }
}
