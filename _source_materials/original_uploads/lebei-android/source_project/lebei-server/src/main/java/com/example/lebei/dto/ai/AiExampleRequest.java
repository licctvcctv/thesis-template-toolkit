package com.example.lebei.dto.ai;

import jakarta.validation.constraints.NotBlank;

public class AiExampleRequest {

    @NotBlank
    private String word;

    private String phonetic;

    @NotBlank
    private String translation;

    public String getWord() {
        return word;
    }

    public void setWord(String word) {
        this.word = word;
    }

    public String getPhonetic() {
        return phonetic;
    }

    public void setPhonetic(String phonetic) {
        this.phonetic = phonetic;
    }

    public String getTranslation() {
        return translation;
    }

    public void setTranslation(String translation) {
        this.translation = translation;
    }
}
