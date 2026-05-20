package com.example.lebei;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.lebei.api.AuthResponse;
import com.example.lebei.api.LebeiApi;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class RegisterActivity extends AppCompatActivity {

    private ExecutorService executor;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        EditText et_username = findViewById(R.id.et_username);
        EditText et_password = findViewById(R.id.et_password);
        EditText et_confirm_password = findViewById(R.id.et_confirm_password);
        Button btn_register = findViewById(R.id.btn_register);

        executor = Executors.newSingleThreadExecutor();
        sessionManager = new SessionManager(this);

        btn_register.setOnClickListener(
                v -> {
                    String username = et_username.getText().toString().trim();
                    String password = et_password.getText().toString().trim();
                    String confirmPassword = et_confirm_password.getText().toString().trim();

                    if (username.length() < 6 || username.length() > 14) {
                        Toast.makeText(this, "用户名必须 6~14 位", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    if (!username.matches("[a-zA-Z0-9]+")) {
                        Toast.makeText(this, "用户名只能是字母/数字", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    if (password.length() < 8) {
                        Toast.makeText(this, "密码至少 8 位", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    int typeCount = checkPasswordType(password);
                    if (typeCount < 2) {
                        Toast.makeText(
                                        this,
                                        "密码必须包含至少两种组合：字母+数字/字母+符号/数字+符号",
                                        Toast.LENGTH_LONG)
                                .show();
                        return;
                    }

                    if (!password.equals(confirmPassword)) {
                        Toast.makeText(this, "两次输入的密码不一致", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    executor.execute(
                            () -> {
                                try {
                                    AuthResponse res = new LebeiApi().register(username, password);
                                    if (res == null || res.token == null || res.token.isEmpty()) {
                                        runOnUiThread(
                                                () ->
                                                        Toast.makeText(
                                                                        RegisterActivity.this,
                                                                        "注册返回数据异常，请稍后重试",
                                                                        Toast.LENGTH_SHORT)
                                                                .show());
                                        return;
                                    }
                                    final AuthResponse resFinal = res;
                                    runOnUiThread(
                                            () -> {
                                                if (isFinishing()) {
                                                    return;
                                                }
                                                sessionManager.saveSession(resFinal.token, resFinal.user);
                                                Toast.makeText(this, "注册成功！", Toast.LENGTH_SHORT).show();
                                                startActivity(
                                                        new Intent(RegisterActivity.this, ProfileSetupActivity.class));
                                                finish();
                                            });
                                } catch (IOException e) {
                                    runOnUiThread(
                                            () ->
                                                    Toast.makeText(
                                                                    this,
                                                                    e.getMessage() != null ? e.getMessage() : "网络错误",
                                                                    Toast.LENGTH_SHORT)
                                                            .show());
                                }
                            });
                });
    }

    private int checkPasswordType(String password) {
        boolean hasLetter = false, hasDigit = false, hasSymbol = false;
        for (char c : password.toCharArray()) {
            if (Character.isLetter(c)) {
                hasLetter = true;
            } else if (Character.isDigit(c)) {
                hasDigit = true;
            } else {
                hasSymbol = true;
            }
        }
        int count = 0;
        if (hasLetter) {
            count++;
        }
        if (hasDigit) {
            count++;
        }
        if (hasSymbol) {
            count++;
        }
        return count;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdown();
    }
}
