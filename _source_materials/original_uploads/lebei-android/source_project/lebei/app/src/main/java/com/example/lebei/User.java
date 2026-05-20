package com.example.lebei;

import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "user")
public class User {
    @PrimaryKey(autoGenerate = true)
    public int id;

    public String username;
    public String password; // 存加密后的密码
    public int ageGroup;            // 1-儿童，2-青少年，3-成人
    public String level;            // "junior", "senior", "cet4", "cet6"
    public String currentBookId;    // 当前选择的词库ID
    public boolean isProfileComplete; // 是否已完成信息设置

    public int dailyNewWords;       // 每日新词数
    public int dailyReviewWords;    // 每日复习词数
}