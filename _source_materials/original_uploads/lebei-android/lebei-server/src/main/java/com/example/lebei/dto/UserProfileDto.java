package com.example.lebei.dto;

public class UserProfileDto {

    private Long id;
    private String username;
    private Integer ageGroup;
    private String level;
    private String currentBookId;
    private Boolean profileComplete;
    private Integer dailyNewWords;
    private Integer dailyReviewWords;
    private Integer learnedWordsCount;
    private Integer masteredWordsCount;

    private Integer studyPoints;
    private Integer todayLearnedCount;

    /** APP_USER 或 ADMIN */
    private String role;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public Integer getAgeGroup() {
        return ageGroup;
    }

    public void setAgeGroup(Integer ageGroup) {
        this.ageGroup = ageGroup;
    }

    public String getLevel() {
        return level;
    }

    public void setLevel(String level) {
        this.level = level;
    }

    public String getCurrentBookId() {
        return currentBookId;
    }

    public void setCurrentBookId(String currentBookId) {
        this.currentBookId = currentBookId;
    }

    public Boolean getProfileComplete() {
        return profileComplete;
    }

    public void setProfileComplete(Boolean profileComplete) {
        this.profileComplete = profileComplete;
    }

    public Integer getDailyNewWords() {
        return dailyNewWords;
    }

    public void setDailyNewWords(Integer dailyNewWords) {
        this.dailyNewWords = dailyNewWords;
    }

    public Integer getDailyReviewWords() {
        return dailyReviewWords;
    }

    public void setDailyReviewWords(Integer dailyReviewWords) {
        this.dailyReviewWords = dailyReviewWords;
    }

    public Integer getLearnedWordsCount() {
        return learnedWordsCount;
    }

    public void setLearnedWordsCount(Integer learnedWordsCount) {
        this.learnedWordsCount = learnedWordsCount;
    }

    public Integer getMasteredWordsCount() {
        return masteredWordsCount;
    }

    public void setMasteredWordsCount(Integer masteredWordsCount) {
        this.masteredWordsCount = masteredWordsCount;
    }

    public Integer getStudyPoints() {
        return studyPoints;
    }

    public void setStudyPoints(Integer studyPoints) {
        this.studyPoints = studyPoints;
    }

    public Integer getTodayLearnedCount() {
        return todayLearnedCount;
    }

    public void setTodayLearnedCount(Integer todayLearnedCount) {
        this.todayLearnedCount = todayLearnedCount;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }
}
