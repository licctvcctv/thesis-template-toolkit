package com.example.lebei;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.example.lebei.api.LebeiApi;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class StatisticsFragment extends Fragment {

    private TextView tvTotalLearned, tvMasteredWords, tvTotalReviews, tvStudyDays;
    private AppDatabase db;
    private ExecutorService executor;
    private SessionManager sessionManager;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_statistics, container, false);

        tvTotalLearned = view.findViewById(R.id.tv_total_learned);
        tvMasteredWords = view.findViewById(R.id.tv_mastered_words);
        tvTotalReviews = view.findViewById(R.id.tv_total_reviews);
        tvStudyDays = view.findViewById(R.id.tv_study_days);

        Button btnLeaderboard = view.findViewById(R.id.btn_leaderboard);
        Button btnSpellingGame = view.findViewById(R.id.btn_spelling_game);
        Button btnGuide = view.findViewById(R.id.btn_statistics_guide);
        db = AppDatabase.getInstance(requireContext());
        executor = Executors.newSingleThreadExecutor();
        sessionManager = new SessionManager(requireContext());

        btnLeaderboard.setOnClickListener(
                v -> {
                    if (sessionManager.getToken() == null) {
                        Toast.makeText(requireContext(), "请先登录", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    startActivity(new Intent(requireContext(), LeaderboardActivity.class));
                });

        btnSpellingGame.setOnClickListener(
                v -> {
                    if (sessionManager.getToken() == null) {
                        Toast.makeText(requireContext(), "请先登录", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    startActivity(new Intent(requireContext(), SpellingGameActivity.class));
                });

        btnGuide.setOnClickListener(
                v ->
                        PageGuideDialog.show(
                                requireContext(), "统计页使用说明", TutorialContent.statisticsGuide()));
        view.post(
                () -> {
                    if (isAdded()) {
                        PageGuideDialog.showOnce(
                                requireContext(),
                                "statistics",
                                "统计页使用说明",
                                TutorialContent.statisticsGuide());
                    }
                });

        loadStatistics();

        return view;
    }

    private void loadStatistics() {
        executor.execute(
                () -> {
                    final int[] totalLearned = new int[1];
                    final int[] mastered = new int[1];
                    final int[] totalReviews = new int[1];
                    final int[] studyDays = new int[1];
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                totalLearned[0] = db.wordDao().getLearnedWordsCount();
                                mastered[0] = db.wordDao().getMasteredWordsCount();
                                totalReviews[0] = db.wordDao().getTotalReviewsCount();
                                long firstLearnTime = db.wordDao().getFirstLearnTime();
                                studyDays[0] = 0;
                                if (firstLearnTime > 0) {
                                    long now = System.currentTimeMillis();
                                    studyDays[0] =
                                            (int) ((now - firstLearnTime) / (24 * 60 * 60 * 1000L)) + 1;
                                }
                            });

                    LebeiApi.syncLearningStatsCount(requireContext(), totalLearned[0], mastered[0]);

                    int finalTotalLearned = totalLearned[0];
                    int finalMastered = mastered[0];
                    int finalTotalReviews = totalReviews[0];
                    int finalStudyDays = studyDays[0];

                    requireActivity()
                            .runOnUiThread(
                                    () -> {
                                        tvTotalLearned.setText(String.valueOf(finalTotalLearned));
                                        tvMasteredWords.setText(String.valueOf(finalMastered));
                                        tvTotalReviews.setText(String.valueOf(finalTotalReviews));
                                        tvStudyDays.setText(String.valueOf(finalStudyDays));
                                    });
                });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        executor.shutdown();
    }
}
