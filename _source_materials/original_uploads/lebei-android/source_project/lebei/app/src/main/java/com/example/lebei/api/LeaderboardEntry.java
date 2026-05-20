package com.example.lebei.api;

/** App 排行榜列表项（与服务端 JSON 字段一致） */
public class LeaderboardEntry {

    private int rank;
    private String username;
    private int learnedWordsCount;
    private int masteredWordsCount;
    private int studyPoints;
    private int todayLearnedCount;

    public int getRank() {
        return rank;
    }

    public String getUsername() {
        return username != null ? username : "";
    }

    public int getLearnedWordsCount() {
        return learnedWordsCount;
    }

    public int getMasteredWordsCount() {
        return masteredWordsCount;
    }

    public int getStudyPoints() {
        return studyPoints;
    }

    public int getTodayLearnedCount() {
        return todayLearnedCount;
    }
}
