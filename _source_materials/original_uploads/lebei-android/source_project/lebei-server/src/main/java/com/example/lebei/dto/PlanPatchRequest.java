package com.example.lebei.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class PlanPatchRequest {

    @NotBlank
    private String currentBookId;

    @NotNull
    @Min(1)
    private Integer dailyNewWords;

    @NotNull
    @Min(1)
    private Integer dailyReviewWords;

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
}
