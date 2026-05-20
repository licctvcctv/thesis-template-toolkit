package com.example.lebei;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentActivity;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class DailyHistoryFragment extends Fragment {

    private RecyclerView recyclerView;
    private TextView hintView;
    private DailyPlanListAdapter adapter;
    private ExecutorService executor;

    @Nullable
    @Override
    public View onCreateView(
            @NonNull LayoutInflater inflater,
            @Nullable ViewGroup container,
            @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_daily_history, container, false);
        recyclerView = view.findViewById(R.id.rv_daily_plans);
        hintView = view.findViewById(R.id.tv_history_hint);
        Button btnGuide = view.findViewById(R.id.btn_history_guide);
        recyclerView.setLayoutManager(new LinearLayoutManager(requireContext()));
        adapter = new DailyPlanListAdapter();
        adapter.setOnPlanClickListener(
                planId -> {
                    Bundle b = new Bundle();
                    b.putLong("planId", planId);
                    Navigation.findNavController(requireView())
                            .navigate(
                                    R.id.action_navigation_daily_review_to_navigation_daily_review_detail,
                                    b);
                });
        recyclerView.setAdapter(adapter);
        executor = Executors.newSingleThreadExecutor();
        btnGuide.setOnClickListener(
                v ->
                        PageGuideDialog.show(
                                requireContext(), "回顾页使用说明", TutorialContent.historyGuide()));
        view.post(
                () -> {
                    if (isAdded()) {
                        PageGuideDialog.showOnce(
                                requireContext(),
                                "history",
                                "回顾页使用说明",
                                TutorialContent.historyGuide());
                    }
                });
        return view;
    }

    @Override
    public void onResume() {
        super.onResume();
        loadPlans();
    }

    private void loadPlans() {
        AppDatabase db = AppDatabase.getInstance(requireContext());
        executor.execute(
                () -> {
                    final List<DailyPlanListAdapter.Row> rows = new ArrayList<>();
                    LocalLearningDataStore.withDbLock(
                            () -> {
                                List<DailyPlan> plans = db.dailyPlanDao().listPlansNewestFirst();
                                if (plans != null) {
                                    for (DailyPlan p : plans) {
                                        int n = db.dailyPlanDao().countWordsInPlan(p.id);
                                        rows.add(new DailyPlanListAdapter.Row(p, n));
                                    }
                                }
                            });
                    if (!isAdded() || getActivity() == null) {
                        return;
                    }
                    FragmentActivity act = requireActivity();
                    act.runOnUiThread(
                            () -> {
                                if (!isAdded() || adapter == null || hintView == null) {
                                    return;
                                }
                                adapter.setData(rows);
                                if (rows.isEmpty()) {
                                    hintView.setText(
                                            "暂无历史记录。在学习页完成当日学习并生成例句/短文后会出现在这里。");
                                }
                            });
                });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        executor.shutdown();
    }
}
