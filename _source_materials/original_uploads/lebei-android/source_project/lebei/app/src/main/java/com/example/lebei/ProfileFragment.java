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
import com.example.lebei.api.UserProfile;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ProfileFragment extends Fragment {

    private TextView tvUsername, tvCurrentBook, tvDailyPlan;
    private Button btnLogout;
    private ExecutorService executor;
    private SessionManager sessionManager;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_profile, container, false);

        tvUsername = view.findViewById(R.id.tv_username);
        tvCurrentBook = view.findViewById(R.id.tv_current_book);
        tvDailyPlan = view.findViewById(R.id.tv_daily_plan);
        btnLogout = view.findViewById(R.id.btn_logout);

        executor = Executors.newSingleThreadExecutor();
        sessionManager = new SessionManager(requireContext());

        loadUserInfo();

        btnLogout.setOnClickListener(v -> logout());

        return view;
    }

    private void loadUserInfo() {
        executor.execute(
                () -> {
                    UserProfile user = sessionManager.getProfile();
                    if (user == null && sessionManager.getToken() != null) {
                        try {
                            user = new LebeiApi().getMe(sessionManager.getToken());
                            sessionManager.saveProfile(user);
                        } catch (IOException ignored) {
                        }
                    }
                    if (user == null) {
                        return;
                    }
                    String bookName = mapBookIdToName(user.currentBookId);
                    String planInfo =
                            "每日新词 " + user.dailyNewWords + " 个，复习 " + user.dailyReviewWords + " 个";

                    UserProfile finalUser = user;
                    requireActivity()
                            .runOnUiThread(
                                    () -> {
                                        tvUsername.setText(finalUser.username);
                                        tvCurrentBook.setText(bookName);
                                        tvDailyPlan.setText(planInfo);
                                    });
                });
    }

    private String mapBookIdToName(String bookId) {
        if (bookId == null) {
            return "—";
        }
        switch (bookId) {
            case "JUNIOR_HIGH":
                return "初中词汇";
            case "SENIOR_HIGH":
                return "高中词汇";
            case "CET4":
                return "大学英语四级";
            case "CET6":
                return "大学英语六级";
            case "IELTS":
                return "雅思词汇";
            case "TOEFL":
                return "托福词汇";
            default:
                return bookId;
        }
    }

    private void logout() {
        sessionManager.logout();
        Toast.makeText(getContext(), "已退出登录", Toast.LENGTH_SHORT).show();
        Intent intent = new Intent(getActivity(), LoginActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        requireActivity().finish();
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        executor.shutdown();
    }
}
