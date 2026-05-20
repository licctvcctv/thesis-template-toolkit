package com.example.lebei.api;

/** Mirrors server {@code UserProfileDto} JSON（App 用户为 APP_USER）. */
public class UserProfile {
    public long id;
    public String username;
    public Integer ageGroup;
    public String level;
    public String currentBookId;
    public boolean profileComplete;
    public int dailyNewWords;
    public int dailyReviewWords;
    public int learnedWordsCount;
    /** App 本地按权重 > 5 统计的已掌握词汇数 */
    public int masteredWordsCount;
    /** 服务端累计积分（每完成一词学习 +1） */
    public int studyPoints;
    /** 服务端当前自然日已完成学习次数 */
    public int todayLearnedCount;
    public String role;
}
