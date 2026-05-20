package com.example.lebei.dto.ai;

public class AiEssayResponse {

    private String content;

    public AiEssayResponse() {}

    public AiEssayResponse(String content) {
        this.content = content;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }
}
