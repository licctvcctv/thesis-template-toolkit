package com.example.lebei;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentActivity;
import com.example.lebei.api.LebeiApi;
import com.example.lebei.api.UserProfile;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class PlanFragment extends Fragment {

    private Spinner spinnerBook;
    private EditText etNewWords, etReviewWords;
    private Button btnSave, btnGuide;
    private TextView tvCurrentPlan;
    private ExecutorService executor;
    private SessionManager sessionManager;

    private final String[] bookNames = {"初中词汇", "高中词汇", "大学英语四级", "大学英语六级", "雅思词汇", "托福词汇"};
    private final String[] bookIds = {"JUNIOR_HIGH", "SENIOR_HIGH", "CET4", "CET6", "IELTS", "TOEFL"};

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_plan, container, false);

        spinnerBook = view.findViewById(R.id.spinner_book);
        etNewWords = view.findViewById(R.id.et_daily_new_words);
        etReviewWords = view.findViewById(R.id.et_daily_review_words);
        btnSave = view.findViewById(R.id.btn_save_plan);
        btnGuide = view.findViewById(R.id.btn_plan_guide);
        tvCurrentPlan = view.findViewById(R.id.tv_current_plan);

        executor = Executors.newSingleThreadExecutor();
        sessionManager = new SessionManager(requireContext());

        ArrayAdapter<String> adapter =
                new ArrayAdapter<>(requireContext(), android.R.layout.simple_spinner_item, bookNames);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerBook.setAdapter(adapter);

        loadCurrentPlan();

        btnGuide.setOnClickListener(
                v ->
                        PageGuideDialog.show(
                                requireContext(), "计划页使用说明", TutorialContent.planGuide()));
        view.post(
                () -> {
                    if (isAdded()) {
                        PageGuideDialog.showOnce(
                                requireContext(),
                                "plan",
                                "计划页使用说明",
                                TutorialContent.planGuide());
                    }
                });
        btnSave.setOnClickListener(v -> savePlan());

        return view;
    }

    private void loadCurrentPlan() {
        executor.execute(
                () -> {
                    UserProfile cached = sessionManager.getProfile();
                    if (cached == null && sessionManager.getToken() != null) {
                        try {
                            cached = new LebeiApi().getMe(sessionManager.getToken());
                            if (cached != null) {
                                sessionManager.saveProfile(cached);
                            }
                        } catch (IOException ignored) {
                        }
                    }
                    UserProfile user = cached;
                    FragmentActivity act = getActivity();
                    if (act == null || !isAdded()) {
                        return;
                    }
                    act.runOnUiThread(
                                    () -> {
                                        if (!isAdded() || getContext() == null) {
                                            return;
                                        }
                                        if (user != null) {
                                            etNewWords.setText(String.valueOf(user.dailyNewWords));
                                            etReviewWords.setText(String.valueOf(user.dailyReviewWords));
                                            String currentBookId =
                                                    user.currentBookId != null ? user.currentBookId : "CET4";
                                            int position = 0;
                                            for (int i = 0; i < bookIds.length; i++) {
                                                if (bookIds[i].equals(currentBookId)) {
                                                    position = i;
                                                    break;
                                                }
                                            }
                                            spinnerBook.setSelection(position);
                                            String bookName = bookNames[position];
                                            tvCurrentPlan.setText(
                                                    "当前计划：词库「"
                                                            + bookName
                                                            + "」，每日新词 "
                                                            + user.dailyNewWords
                                                            + " 个，复习 "
                                                            + user.dailyReviewWords
                                                            + " 个");
                                        }
                                    });
                });
    }

    private void savePlan() {
        String newStr = etNewWords.getText().toString().trim();
        String reviewStr = etReviewWords.getText().toString().trim();

        if (newStr.isEmpty() || reviewStr.isEmpty()) {
            Toast.makeText(getContext(), "请输入有效数字", Toast.LENGTH_SHORT).show();
            return;
        }

        int newNum = Integer.parseInt(newStr);
        int reviewNum = Integer.parseInt(reviewStr);

        int selectedPosition = spinnerBook.getSelectedItemPosition();
        String selectedBookId = bookIds[selectedPosition];
        String selectedBookName = bookNames[selectedPosition];

        String token = sessionManager.getToken();
        if (token == null) {
            Toast.makeText(getContext(), "请重新登录", Toast.LENGTH_SHORT).show();
            return;
        }

        executor.execute(
                () -> {
                    try {
                        UserProfile updated =
                                new LebeiApi().updatePlan(token, selectedBookId, newNum, reviewNum);
                        sessionManager.saveProfile(updated);
                        FragmentActivity act = getActivity();
                        if (act != null && isAdded()) {
                            act.runOnUiThread(
                                    () -> {
                                        if (!isAdded() || getContext() == null) {
                                            return;
                                        }
                                        Toast.makeText(getContext(), "计划保存成功", Toast.LENGTH_SHORT).show();
                                        tvCurrentPlan.setText(
                                                "当前计划：词库「"
                                                        + selectedBookName
                                                        + "」，每日新词 "
                                                        + newNum
                                                        + " 个，复习 "
                                                        + reviewNum
                                                        + " 个");
                                    });
                        }
                    } catch (IOException e) {
                        FragmentActivity actE = getActivity();
                        if (actE != null && isAdded()) {
                            actE.runOnUiThread(
                                    () -> {
                                        if (!isAdded() || getContext() == null) {
                                            return;
                                        }
                                        Toast.makeText(
                                                        getContext(),
                                                        e.getMessage() != null ? e.getMessage() : "保存失败",
                                                        Toast.LENGTH_SHORT)
                                                .show();
                                    });
                        }
                    }
                });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        executor.shutdown();
    }
}
