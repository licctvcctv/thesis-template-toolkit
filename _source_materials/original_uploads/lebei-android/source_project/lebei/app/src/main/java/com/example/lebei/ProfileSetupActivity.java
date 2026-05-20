package com.example.lebei;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.lebei.api.LebeiApi;
import com.example.lebei.api.UserProfile;
import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ProfileSetupActivity extends AppCompatActivity {

    private RadioGroup rgAge, rgLevel;
    private Spinner spinnerBook;
    private Button btnFinish;
    private ExecutorService executor;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_profile_setup);

        sessionManager = new SessionManager(this);
        if (sessionManager.getToken() == null) {
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        rgAge = findViewById(R.id.rg_age_group);
        rgLevel = findViewById(R.id.rg_level);
        spinnerBook = findViewById(R.id.spinner_book);
        btnFinish = findViewById(R.id.btn_finish_setup);

        executor = Executors.newSingleThreadExecutor();

        String[] books = {"初中词汇", "高中词汇", "大学英语四级", "大学英语六级", "雅思词汇", "托福词汇"};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, books);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerBook.setAdapter(adapter);

        btnFinish.setOnClickListener(v -> saveProfileAndFinish());
    }

    private void saveProfileAndFinish() {
        int ageGroup = 0;
        int selectedAgeId = rgAge.getCheckedRadioButtonId();
        if (selectedAgeId == R.id.rb_child) {
            ageGroup = 1;
        } else if (selectedAgeId == R.id.rb_teen) {
            ageGroup = 2;
        } else if (selectedAgeId == R.id.rb_adult) {
            ageGroup = 3;
        }

        if (ageGroup == 0) {
            Toast.makeText(this, "请选择年龄段", Toast.LENGTH_SHORT).show();
            return;
        }

        String level = "";
        int selectedLevelId = rgLevel.getCheckedRadioButtonId();
        if (selectedLevelId == R.id.rb_junior) {
            level = "junior";
        } else if (selectedLevelId == R.id.rb_senior) {
            level = "senior";
        } else if (selectedLevelId == R.id.rb_cet4) {
            level = "cet4";
        } else if (selectedLevelId == R.id.rb_cet6) {
            level = "cet6";
        }

        if (level.isEmpty()) {
            Toast.makeText(this, "请选择英语水平", Toast.LENGTH_SHORT).show();
            return;
        }

        String bookName = spinnerBook.getSelectedItem().toString();
        String bookId = mapBookNameToId(bookName);

        final int finalAgeGroup = ageGroup;
        final String finalLevel = level;
        final String finalBookId = bookId;

        executor.execute(
                () -> {
                    try {
                        UserProfile updated =
                                new LebeiApi()
                                        .updateProfile(
                                                sessionManager.getToken(),
                                                finalAgeGroup,
                                                finalLevel,
                                                finalBookId,
                                                10,
                                                20,
                                                true);
                        sessionManager.saveProfile(updated);
                        runOnUiThread(
                                () -> {
                                    Toast.makeText(ProfileSetupActivity.this, "设置完成！", Toast.LENGTH_SHORT)
                                            .show();
                                    startActivity(new Intent(ProfileSetupActivity.this, MainActivity.class));
                                    finish();
                                });
                    } catch (IOException e) {
                        runOnUiThread(
                                () ->
                                        Toast.makeText(
                                                        ProfileSetupActivity.this,
                                                        e.getMessage() != null ? e.getMessage() : "保存失败",
                                                        Toast.LENGTH_SHORT)
                                                .show());
                    }
                });
    }

    private String mapBookNameToId(String bookName) {
        switch (bookName) {
            case "初中词汇":
                return "JUNIOR_HIGH";
            case "高中词汇":
                return "SENIOR_HIGH";
            case "大学英语四级":
                return "CET4";
            case "大学英语六级":
                return "CET6";
            case "雅思词汇":
                return "IELTS";
            case "托福词汇":
                return "TOEFL";
            default:
                return "CET4";
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdown();
    }
}
