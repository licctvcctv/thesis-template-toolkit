package com.example.lebei.controller.app;

import com.example.lebei.dto.ai.AiEssayRequest;
import com.example.lebei.dto.ai.AiEssayResponse;
import com.example.lebei.dto.ai.AiExampleRequest;
import com.example.lebei.dto.ai.AiExampleResponse;
import com.example.lebei.service.AiService;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/app/ai")
public class AppAiController {

    private final AiService aiService;

    public AppAiController(AiService aiService) {
        this.aiService = aiService;
    }

    @PostMapping("/example")
    public AiExampleResponse example(Authentication authentication, @Valid @RequestBody AiExampleRequest body) {
        Long userId = (Long) authentication.getPrincipal();
        String text =
                aiService.generateExample(
                        userId,
                        body.getWord(),
                        body.getPhonetic() != null ? body.getPhonetic() : "",
                        body.getTranslation());
        return new AiExampleResponse(text);
    }

    @PostMapping("/essay")
    public AiEssayResponse essay(Authentication authentication, @Valid @RequestBody AiEssayRequest body) {
        Long userId = (Long) authentication.getPrincipal();
        String text = aiService.generateEssay(userId, body.getWords());
        return new AiEssayResponse(text);
    }
}
