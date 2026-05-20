package com.example.lebei;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.lebei.api.AuthResponse;
import com.example.lebei.api.LebeiApi;
import com.example.lebei.api.UserProfile;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class LoginActivity extends AppCompatActivity {

    private EditText etUsername, etPassword;
    private Button btnLogin;
    private TextView tvToRegister;
    private ExecutorService executor;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        etUsername = findViewById(R.id.et_login_username);
        etPassword = findViewById(R.id.et_login_password);
        btnLogin = findViewById(R.id.btn_login);
        tvToRegister = findViewById(R.id.tv_to_register);

        executor = Executors.newSingleThreadExecutor();
        sessionManager = new SessionManager(this);

        if (sessionManager.getToken() != null) {
            executor.execute(
                    () -> {
                        try {
                            UserProfile p = new LebeiApi().getMe(sessionManager.getToken());
                            runOnUiThread(
                                    () -> {
                                        if (isFinishing()) {
                                            return;
                                        }
                                        if (p != null) {
                                            sessionManager.saveProfile(p);
                                        }
                                        goAfterLogin(p);
                                        finish();
                                    });
                        } catch (IOException e) {
                            runOnUiThread(
                                    () -> {
                                        sessionManager.logout();
                                        Toast.makeText(LoginActivity.this, "登录已失效，请重新登录", Toast.LENGTH_SHORT)
                                                .show();
                                    });
                        }
                    });
        }

        btnLogin.setOnClickListener(
                view -> {
                    String username = etUsername.getText().toString().trim();
                    String password = etPassword.getText().toString().trim();

                    if (username.isEmpty()) {
                        Toast.makeText(LoginActivity.this, "请输入用户名", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    if (password.isEmpty()) {
                        Toast.makeText(LoginActivity.this, "请输入密码", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    executor.execute(
                            () -> {
                                try {
                                    AuthResponse res = new LebeiApi().login(username, password);
                                    if (res == null || res.token == null || res.token.isEmpty()) {
                                        runOnUiThread(
                                                () ->
                                                        Toast.makeText(
                                                                        LoginActivity.this,
                                                                        "登录返回数据异常，请稍后重试",
                                                                        Toast.LENGTH_SHORT)
                                                                .show());
                                        return;
                                    }
                                    // 在主线程写会话，避免刚进入 MainActivity 时子线程读不到 token/profile 导致闪退
                                    final AuthResponse resFinal = res;
                                    runOnUiThread(
                                            () -> {
                                                if (isFinishing()) {
                                                    return;
                                                }
                                                sessionManager.saveSession(resFinal.token, resFinal.user);
                                                Toast.makeText(LoginActivity.this, "登录成功！", Toast.LENGTH_SHORT)
                                                        .show();
                                                goAfterLogin(resFinal.user);
                                                finish();
                                            });
                                } catch (IOException e) {
                                    runOnUiThread(
                                            () ->
                                                    Toast.makeText(
                                                                    LoginActivity.this,
                                                                    e.getMessage() != null ? e.getMessage() : "网络错误",
                                                                    Toast.LENGTH_SHORT)
                                                            .show());
                                }
                            });
                });

        tvToRegister.setOnClickListener(
                view -> startActivity(new Intent(LoginActivity.this, RegisterActivity.class)));
    }

    private void goAfterLogin(UserProfile user) {
        if (user == null || !user.profileComplete) {
            startActivity(new Intent(this, ProfileSetupActivity.class));
        } else {
            startActivity(new Intent(this, MainActivity.class));
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdown();
    }
}
