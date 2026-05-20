package com.example.lebei;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import com.example.lebei.api.LebeiApi;
import com.example.lebei.api.UserProfile;
import com.google.android.material.appbar.MaterialToolbar;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SpellingGameActivity extends AppCompatActivity {

    private static final int GAME_WORD_LIMIT = 80;

    private final Handler timerHandler = new Handler(Looper.getMainLooper());
    private final List<Word> gameWords = new ArrayList<>();

    private ProgressBar progressLoading;
    private TextView tvEmpty;
    private LinearLayout gameContent;
    private TextView tvTimer;
    private TextView tvScore;
    private TextView tvProgress;
    private TextView tvTranslation;
    private TextView tvPhonetic;
    private EditText etAnswer;
    private Button btnSubmit;
    private Button btnSkip;
    private TextView tvFeedback;
    private TextView tvResult;
    private LinearLayout resultActions;
    private Button btnReplay;
    private Button btnLeaderboard;

    private AppDatabase db;
    private SessionManager sessionManager;
    private ExecutorService executor;
    private int currentIndex;
    private int score;
    private int answered;
    private long startedAtMs;
    private boolean gameOver;

    private final Runnable timerTick =
            new Runnable() {
                @Override
                public void run() {
                    if (gameOver) {
                        return;
                    }
                    long now = System.currentTimeMillis();
                    long remaining = Math.max(0L, SpellingGamePolicy.GAME_DURATION_MS - (now - startedAtMs));
                    tvTimer.setText(formatRemaining(remaining));
                    if (SpellingGamePolicy.isTimeUp(startedAtMs, now)) {
                        endGame("时间到，本局挑战结束");
                    } else {
                        timerHandler.postDelayed(this, 250L);
                    }
                }
            };

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_spelling_game);

        sessionManager = new SessionManager(this);
        if (sessionManager.getToken() == null) {
            Toast.makeText(this, "请先登录", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        db = AppDatabase.getInstance(this);
        executor = Executors.newSingleThreadExecutor();

        MaterialToolbar toolbar = findViewById(R.id.toolbar_game);
        toolbar.setNavigationOnClickListener(v -> getOnBackPressedDispatcher().onBackPressed());

        bindViews();
        bindActions();
        loadWordsAndStart();
    }

    private void bindViews() {
        progressLoading = findViewById(R.id.progress_game_loading);
        tvEmpty = findViewById(R.id.tv_game_empty);
        gameContent = findViewById(R.id.ll_game_content);
        tvTimer = findViewById(R.id.tv_game_timer);
        tvScore = findViewById(R.id.tv_game_score);
        tvProgress = findViewById(R.id.tv_game_progress);
        tvTranslation = findViewById(R.id.tv_game_translation);
        tvPhonetic = findViewById(R.id.tv_game_phonetic);
        etAnswer = findViewById(R.id.et_game_answer);
        btnSubmit = findViewById(R.id.btn_game_submit);
        btnSkip = findViewById(R.id.btn_game_skip);
        tvFeedback = findViewById(R.id.tv_game_feedback);
        tvResult = findViewById(R.id.tv_game_result);
        resultActions = findViewById(R.id.ll_game_result_actions);
        btnReplay = findViewById(R.id.btn_game_replay);
        btnLeaderboard = findViewById(R.id.btn_game_leaderboard);
    }

    private void bindActions() {
        btnSubmit.setOnClickListener(v -> submitAnswer());
        btnSkip.setOnClickListener(v -> skipWord());
        btnReplay.setOnClickListener(v -> loadWordsAndStart());
        btnLeaderboard.setOnClickListener(v -> startActivity(new Intent(this, LeaderboardActivity.class)));
    }

    private void loadWordsAndStart() {
        showLoading();
        executor.execute(
                () -> {
                    List<Word> loaded = new ArrayList<>();
                    long now = System.currentTimeMillis();
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                db.wordDao().decayMasteredWords(now);
                                appendUnique(loaded, db.wordDao().getGameDueWords(now, GAME_WORD_LIMIT));
                                if (loaded.size() < GAME_WORD_LIMIT) {
                                    appendUnique(
                                            loaded,
                                            db.wordDao().getGameLearnedWords(GAME_WORD_LIMIT * 2));
                                }
                            });

                    runOnUiThread(
                            () -> {
                                gameWords.clear();
                                gameWords.addAll(loaded);
                                if (gameWords.isEmpty()) {
                                    showEmpty();
                                } else {
                                    startGame();
                                }
                            });
                });
    }

    private static void appendUnique(List<Word> target, List<Word> source) {
        if (source == null || source.isEmpty()) {
            return;
        }
        Set<Integer> seen = new HashSet<>();
        for (Word w : target) {
            seen.add(w.id);
        }
        for (Word w : source) {
            if (w != null && seen.add(w.id)) {
                target.add(w);
                if (target.size() >= GAME_WORD_LIMIT) {
                    return;
                }
            }
        }
    }

    private void showLoading() {
        timerHandler.removeCallbacks(timerTick);
        gameOver = true;
        progressLoading.setVisibility(View.VISIBLE);
        tvEmpty.setVisibility(View.GONE);
        gameContent.setVisibility(View.GONE);
        tvResult.setVisibility(View.GONE);
        resultActions.setVisibility(View.GONE);
    }

    private void showEmpty() {
        progressLoading.setVisibility(View.GONE);
        tvEmpty.setVisibility(View.VISIBLE);
        gameContent.setVisibility(View.GONE);
        tvResult.setVisibility(View.GONE);
        resultActions.setVisibility(View.GONE);
    }

    private void startGame() {
        currentIndex = 0;
        score = 0;
        answered = 0;
        startedAtMs = System.currentTimeMillis();
        gameOver = false;

        progressLoading.setVisibility(View.GONE);
        tvEmpty.setVisibility(View.GONE);
        gameContent.setVisibility(View.VISIBLE);
        tvResult.setVisibility(View.GONE);
        resultActions.setVisibility(View.GONE);
        setControlsEnabled(true);
        tvFeedback.setText("");
        updateScore();
        showWord();
        timerHandler.post(timerTick);
    }

    private void showWord() {
        if (currentIndex >= gameWords.size()) {
            endGame("题库完成，本局挑战结束");
            return;
        }
        Word word = gameWords.get(currentIndex);
        tvProgress.setText(
                String.format(Locale.US, "第 %d / %d 题", currentIndex + 1, gameWords.size()));
        tvTranslation.setText(emptyToFallback(word.translation, "暂无释义"));
        tvPhonetic.setText(emptyToFallback(word.phonetic, "暂无音标"));
        etAnswer.setText("");
        etAnswer.requestFocus();
    }

    private void submitAnswer() {
        if (gameOver) {
            return;
        }
        long now = System.currentTimeMillis();
        if (SpellingGamePolicy.isTimeUp(startedAtMs, now)) {
            endGame("时间到，本局挑战结束");
            return;
        }
        String answer = etAnswer.getText().toString();
        if (WordReviewPolicy.normalizeSpelling(answer).isEmpty()) {
            Toast.makeText(this, "请输入单词拼写", Toast.LENGTH_SHORT).show();
            return;
        }

        Word word = gameWords.get(currentIndex);
        boolean correct = WordReviewPolicy.spellingsMatch(word.word, answer);
        answered = SpellingGamePolicy.answeredAfterSubmit(answered);
        score = SpellingGamePolicy.scoreAfterAnswer(score, correct);
        updateScore();

        if (correct) {
            tvFeedback.setTextColor(Color.parseColor("#2E7D32"));
            tvFeedback.setText("拼写正确，积分 +1");
            persistCorrectAnswer(word);
        } else {
            tvFeedback.setTextColor(Color.parseColor("#C92A2A"));
            tvFeedback.setText("拼写错误，正确拼写：" + word.word);
        }
        moveToNextWord();
    }

    private void skipWord() {
        if (gameOver) {
            return;
        }
        Word word = gameWords.get(currentIndex);
        tvFeedback.setTextColor(Color.parseColor("#5F6368"));
        tvFeedback.setText("已跳过，正确拼写：" + word.word);
        moveToNextWord();
    }

    private void moveToNextWord() {
        currentIndex++;
        if (currentIndex >= gameWords.size()) {
            endGame("题库完成，本局挑战结束");
        } else {
            showWord();
        }
    }

    private void persistCorrectAnswer(Word answeredWord) {
        final String token = sessionManager.getToken();
        if (token == null) {
            return;
        }
        executor.execute(
                () -> {
                    long now = System.currentTimeMillis();
                    int nextWeight =
                            WordReviewPolicy.weightAfterSpellingResult(answeredWord.familiarity, true);
                    answeredWord.familiarity = nextWeight;
                    answeredWord.nextReviewTime = WordReviewPolicy.nextReviewTime(now, nextWeight, true);
                    answeredWord.reviewCount++;

                    final int[] learnedCount = new int[1];
                    final int[] masteredCount = new int[1];
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                db.wordDao().update(answeredWord);
                                learnedCount[0] = db.wordDao().getLearnedWordsCount();
                                masteredCount[0] = db.wordDao().getMasteredWordsCount();
                            });

                    LebeiApi.syncLearningStatsCount(
                            getApplicationContext(), learnedCount[0], masteredCount[0]);
                    try {
                        UserProfile updated = new LebeiApi().recordStudyWord(token);
                        sessionManager.saveProfile(updated);
                    } catch (IOException e) {
                        runOnUiThread(
                                () ->
                                        Toast.makeText(
                                                        this,
                                                        "积分同步失败，稍后再试",
                                                        Toast.LENGTH_SHORT)
                                                .show());
                    }
                });
    }

    private void endGame(String reason) {
        gameOver = true;
        timerHandler.removeCallbacks(timerTick);
        setControlsEnabled(false);
        tvTimer.setText(formatRemaining(0L));
        tvFeedback.setText(reason);
        tvFeedback.setTextColor(Color.parseColor("#5F6368"));
        tvResult.setText(String.format(Locale.US, "本局得分 %d，完成 %d 次拼写", score, answered));
        tvResult.setVisibility(View.VISIBLE);
        resultActions.setVisibility(View.VISIBLE);
    }

    private void setControlsEnabled(boolean enabled) {
        etAnswer.setEnabled(enabled);
        btnSubmit.setEnabled(enabled);
        btnSkip.setEnabled(enabled);
    }

    private void updateScore() {
        tvScore.setText(String.valueOf(score));
    }

    private static String formatRemaining(long remainingMs) {
        long totalSeconds = Math.max(0L, (remainingMs + 999L) / 1000L);
        long minutes = totalSeconds / 60L;
        long seconds = totalSeconds % 60L;
        return String.format(Locale.US, "%02d:%02d", minutes, seconds);
    }

    private static String emptyToFallback(String value, String fallback) {
        if (value == null || value.trim().isEmpty()) {
            return fallback;
        }
        return value;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        timerHandler.removeCallbacks(timerTick);
        if (executor != null) {
            executor.shutdown();
        }
    }
}
