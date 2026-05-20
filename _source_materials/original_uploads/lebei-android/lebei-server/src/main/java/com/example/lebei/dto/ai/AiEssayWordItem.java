package com.example.lebei.dto.ai;

import jakarta.validation.constraints.NotBlank;

public class AiEssayWordItem {

    @NotBlank
    private String word;

    @NotBlank
    private String translation;

    public String getWord() {
        return word;
    }

    public void setWord(String word) {
        this.word = word;
    }

    public String getTranslation() {
        return translation;
    }

    public void setTranslation(String translation) {
        this.translation = translation;
    }
}
