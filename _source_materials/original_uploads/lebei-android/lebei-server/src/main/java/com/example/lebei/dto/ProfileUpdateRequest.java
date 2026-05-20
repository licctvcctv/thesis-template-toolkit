package com.example.lebei.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class ProfileUpdateRequest {

    @NotNull
    @Min(1)
    @Max(3)
    private Integer ageGroup;

    @NotNull
    private String level;

    @NotNull
    private String currentBookId;

    private Integer dailyNewWords = 10;
    private Integer dailyReviewWords = 20;

    @NotNull
    private Boolean profileComplete;

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

    public Boolean getProfileComplete() {
        return profileComplete;
    }

    public void setProfileComplete(Boolean profileComplete) {
        this.profileComplete = profileComplete;
    }
}
