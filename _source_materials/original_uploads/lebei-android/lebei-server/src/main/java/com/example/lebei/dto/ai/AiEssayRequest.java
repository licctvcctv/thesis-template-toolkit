package com.example.lebei.dto.ai;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;
import java.util.List;

public class AiEssayRequest {

    @NotEmpty
    @Size(max = 30)
    @Valid
    private List<AiEssayWordItem> words;

    public List<AiEssayWordItem> getWords() {
        return words;
    }

    public void setWords(List<AiEssayWordItem> words) {
        this.words = words;
    }
}
