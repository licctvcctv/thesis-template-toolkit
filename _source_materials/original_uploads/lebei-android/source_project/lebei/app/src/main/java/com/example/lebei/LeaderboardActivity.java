package com.example.lebei;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.lebei.api.LebeiApi;
import com.example.lebei.api.LeaderboardEntry;
import com.google.android.material.appbar.MaterialToolbar;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class LeaderboardActivity extends AppCompatActivity {

    private static final int LEADERBOARD_LIMIT = 100;

    private ProgressBar progress;
    private TextView tvError, tvEmpty;
    private View scrollContent;
    private RecyclerView recycler;
    private LeaderboardAdapter adapter;
    private ExecutorService executor;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_leaderboard);

        SessionManager sm = new SessionManager(this);
        if (sm.getToken() == null) {
            Toast.makeText(this, "请先登录", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        toolbar.setNavigationOnClickListener(v -> getOnBackPressedDispatcher().onBackPressed());

        progress = findViewById(R.id.progress);
        tvError = findViewById(R.id.tv_error);
        tvEmpty = findViewById(R.id.tv_empty);
        scrollContent = findViewById(R.id.scroll_content);
        recycler = findViewById(R.id.recycler_leaderboard);

        adapter = new LeaderboardAdapter();
        recycler.setLayoutManager(new LinearLayoutManager(this));
        recycler.setAdapter(adapter);

        executor = Executors.newSingleThreadExecutor();
        loadLeaderboard(sm.getToken());
    }

    private void loadLeaderboard(String token) {
        progress.setVisibility(View.VISIBLE);
        tvError.setVisibility(View.GONE);
        tvEmpty.setVisibility(View.GONE);
        scrollContent.setVisibility(View.GONE);

        executor.execute(
                () -> {
                    try {
                        List<LeaderboardEntry> list = new LebeiApi().getLeaderboard(token, LEADERBOARD_LIMIT);
                        runOnUiThread(
                                () -> {
                                    progress.setVisibility(View.GONE);
                                    if (list == null || list.isEmpty()) {
                                        tvEmpty.setVisibility(View.VISIBLE);
                                        return;
                                    }
                                    adapter.setRows(list);
                                    scrollContent.setVisibility(View.VISIBLE);
                                });
                    } catch (IOException e) {
                        runOnUiThread(
                                () -> {
                                    progress.setVisibility(View.GONE);
                                    tvError.setText(e.getMessage() != null ? e.getMessage() : "加载失败");
                                    tvError.setVisibility(View.VISIBLE);
                                });
                    }
                });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (executor != null) {
            executor.shutdown();
        }
    }
}
