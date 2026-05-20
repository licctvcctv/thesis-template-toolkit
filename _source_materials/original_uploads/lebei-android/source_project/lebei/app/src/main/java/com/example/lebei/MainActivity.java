package com.example.lebei;

import android.os.Bundle;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.navigation.NavController;
import androidx.navigation.fragment.NavHostFragment;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;
import com.example.lebei.api.LebeiApi;
import com.example.lebei.api.UserProfile;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {

    private ExecutorService executor;
    private AppDatabase db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        executor = Executors.newSingleThreadExecutor();
        db = AppDatabase.getInstance(this);

        SessionManager sm = new SessionManager(this);
        if (sm.getToken() != null) {
            executor.execute(
                    () -> {
                        try {
                            UserProfile p = new LebeiApi().getMe(sm.getToken());
                            sm.saveProfile(p);
                        } catch (IOException ignored) {
                        }
                    });
        }

        // 设置底部导航
        BottomNavigationView navView = findViewById(R.id.nav_view);

        // 安全获取 NavController（避免部分机型/主题下 Fragment 尚未创建导致 NPE 闪退）
        NavHostFragment navHostFragment =
                (NavHostFragment) getSupportFragmentManager().findFragmentById(R.id.nav_host_fragment);
        if (navHostFragment == null) {
            Toast.makeText(this, "主界面加载失败，请重启应用。", Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        NavController navController = navHostFragment.getNavController();

        AppBarConfiguration appBarConfiguration = new AppBarConfiguration.Builder(
                R.id.navigation_learn,
                R.id.navigation_plan,
                R.id.navigation_statistics,
                R.id.navigation_daily_review,
                R.id.navigation_profile)
                .build();

        // 如果主题没有 ActionBar，这行注释掉避免崩溃
        // NavigationUI.setupActionBarWithNavController(this, navController, appBarConfiguration);
        NavigationUI.setupWithNavController(navView, navController);

        // 初始化词库数据，仅执行一次（与换号清空等写库串行，避免 SQLITE_BUSY）
        executor.execute(
                () ->
                        LocalLearningDataStore.withDbLock(
                                () ->
                                        DataProvider.ensureVocabularyFromAssets(MainActivity.this, db)));
    }  // <-- 这里补上了缺失的 onCreate 结束大括号

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (executor != null) {
            executor.shutdown();
        }
    }
}