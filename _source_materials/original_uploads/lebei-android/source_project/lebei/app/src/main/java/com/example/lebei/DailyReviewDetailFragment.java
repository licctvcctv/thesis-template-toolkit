package com.example.lebei;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class DailyReviewDetailFragment extends Fragment {

    private TextView bodyView;
    private ExecutorService executor;
    private long planId;

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Bundle args = getArguments();
        if (args != null) {
            planId = args.getLong("planId", 0L);
        }
    }

    @Nullable
    @Override
    public View onCreateView(
            @NonNull LayoutInflater inflater,
            @Nullable ViewGroup container,
            @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_daily_review_detail, container, false);
        bodyView = view.findViewById(R.id.tv_review_body);
        executor = Executors.newSingleThreadExecutor();
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        if (planId <= 0) {
            bodyView.setText("无效的记录。");
            return;
        }
        bodyView.setText("加载中…");
        AppDatabase db = AppDatabase.getInstance(requireContext());
        executor.execute(
                () -> {
                    final DailyPlan[] planHolder = new DailyPlan[1];
                    final StringBuilder[] textHolder = new StringBuilder[] {new StringBuilder()};
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                DailyPlan plan = db.dailyPlanDao().getPlanById(planId);
                                planHolder[0] = plan;
                                if (plan == null) {
                                    return;
                                }
                                List<DailyPlanWord> rawRows = db.dailyPlanDao().getPlanWords(planId);
                                List<DailyPlanWord> rows =
                                        rawRows != null ? rawRows : new java.util.ArrayList<>();
                                List<Integer> ids = new java.util.ArrayList<>();
                                for (DailyPlanWord r : rows) {
                                    if (r != null) {
                                        ids.add(r.wordId);
                                    }
                                }
                                java.util.Map<Integer, Word> byId = new java.util.HashMap<>();
                                if (!ids.isEmpty()) {
                                    List<Word> words = db.wordDao().getWordsByIdsChunked(ids);
                                    if (words != null) {
                                        for (Word w : words) {
                                            byId.put(w.id, w);
                                        }
                                    }
                                }
                                StringBuilder sb = textHolder[0];
                                DailyPlan p = plan;
                                sb.append(p.dateKey)
                                        .append(" · ")
                                        .append(BookLabels.nameForBookId(p.bookId))
                                        .append("\n\n");
                                if (p.essayText != null && !p.essayText.trim().isEmpty()) {
                                    sb.append("【短文】\n");
                                    sb.append(p.essayText.trim());
                                    sb.append("\n\n");
                                }
                                sb.append("【单词与例句】\n");
                                for (DailyPlanWord r : rows) {
                                    Word w = byId.get(r.wordId);
                                    if (w == null) {
                                        continue;
                                    }
                                    sb.append("— ").append(w.word);
                                    if (w.phonetic != null && !w.phonetic.isEmpty()) {
                                        sb.append(" ").append(w.phonetic);
                                    }
                                    sb.append("\n");
                                    if (w.translation != null && !w.translation.isEmpty()) {
                                        sb.append(w.translation).append("\n");
                                    }
                                    if (r.aiExampleText != null && !r.aiExampleText.trim().isEmpty()) {
                                        sb.append("例句：").append(r.aiExampleText.trim()).append("\n");
                                    }
                                    sb.append("\n");
                                }
                            });
                    DailyPlan plan = planHolder[0];
                    if (plan == null) {
                        if (isAdded() && getActivity() != null) {
                            requireActivity()
                                    .runOnUiThread(
                                            () -> {
                                                if (!isAdded() || bodyView == null) {
                                                    return;
                                                }
                                                Toast.makeText(
                                                                requireContext(),
                                                                "记录不存在",
                                                                Toast.LENGTH_SHORT)
                                                        .show();
                                                bodyView.setText("");
                                            });
                        }
                        return;
                    }

                    String text = textHolder[0].toString().trim();
                    if (isAdded() && getActivity() != null) {
                        requireActivity()
                                .runOnUiThread(
                                        () -> {
                                            if (!isAdded() || bodyView == null) {
                                                return;
                                            }
                                            bodyView.setText(text);
                                        });
                    }
                });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        executor.shutdown();
    }
}
