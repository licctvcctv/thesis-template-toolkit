package com.example.lebei.dto;

public class LeaderboardEntryDto {

    private int rank;
    private String username;
    private int learnedWordsCount;
    /** App 本地按权重 > 5 统计的已掌握词汇数 */
    private int masteredWordsCount;
    /** 累计积分：每完成一次单词学习 +1 */
    private int studyPoints;
    /** 当前自然日已完成学习次数（服务器日期） */
    private int todayLearnedCount;

    public LeaderboardEntryDto() {}

    public LeaderboardEntryDto(
            int rank,
            String username,
            int learnedWordsCount,
            int masteredWordsCount,
            int studyPoints,
            int todayLearnedCount) {
        this.rank = rank;
        this.username = username;
        this.learnedWordsCount = learnedWordsCount;
        this.masteredWordsCount = masteredWordsCount;
        this.studyPoints = studyPoints;
        this.todayLearnedCount = todayLearnedCount;
    }

    public int getRank() {
        return rank;
    }

    public void setRank(int rank) {
        this.rank = rank;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public int getLearnedWordsCount() {
        return learnedWordsCount;
    }

    public void setLearnedWordsCount(int learnedWordsCount) {
        this.learnedWordsCount = learnedWordsCount;
    }

    public int getMasteredWordsCount() {
        return masteredWordsCount;
    }

    public void setMasteredWordsCount(int masteredWordsCount) {
        this.masteredWordsCount = masteredWordsCount;
    }

    public int getStudyPoints() {
        return studyPoints;
    }

    public void setStudyPoints(int studyPoints) {
        this.studyPoints = studyPoints;
    }

    public int getTodayLearnedCount() {
        return todayLearnedCount;
    }

    public void setTodayLearnedCount(int todayLearnedCount) {
        this.todayLearnedCount = todayLearnedCount;
    }
}
