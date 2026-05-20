package com.example.lebei.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public class LearnedWordsSyncRequest {

    @NotNull
    @Min(0)
    private Integer learnedWordsCount;

    @Min(0)
    private Integer masteredWordsCount;

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
}
