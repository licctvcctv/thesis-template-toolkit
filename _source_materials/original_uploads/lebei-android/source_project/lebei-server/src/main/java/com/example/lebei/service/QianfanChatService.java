package com.example.lebei.service;

import com.example.lebei.config.AiProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

/**
 * 千帆 v2 OpenAI 兼容对话：<a href="https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb">官方文档</a>
 * POST https://qianfan.baidubce.com/v2/chat/completions ，Authorization: Bearer &lt;IAM API Key&gt;
 */
@Service
public class QianfanChatService {

    private static final String V2_CHAT_URL = "https://qianfan.baidubce.com/v2/chat/completions";

    private final AiProperties aiProperties;
    private final ObjectMapper objectMapper;
    private final RestClient restClient = RestClient.builder().build();

    public QianfanChatService(AiProperties aiProperties, ObjectMapper objectMapper) {
        this.aiProperties = aiProperties;
        this.objectMapper = objectMapper;
    }

    public String chat(String systemPrompt, String userPrompt) {
        String mis = aiProperties.describeQianfanKeyMisconfiguration();
        if (mis != null) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, mis);
        }
        String apiKey = aiProperties.effectiveQianfanApiKey();

        String model = aiProperties.getQianfanModel() != null ? aiProperties.getQianfanModel().trim() : "ernie-3.5-8k";
        if (model.isEmpty()) {
            model = "ernie-3.5-8k";
        }

        String auth = authorizationHeader(apiKey);

        List<Map<String, String>> messages = new ArrayList<>();
        messages.add(Map.of("role", "system", "content", systemPrompt));
        messages.add(Map.of("role", "user", "content", userPrompt));

        Map<String, Object> body = new LinkedHashMap<>();
        body.put("model", model);
        body.put("messages", messages);
        body.put("temperature", 0.65);
        body.put("top_p", 0.85);
        body.put("stream", false);

        String raw;
        try {
            raw =
                    restClient
                            .post()
                            .uri(V2_CHAT_URL)
                            .contentType(MediaType.APPLICATION_JSON)
                            .header("Authorization", auth)
                            .body(body)
                            .retrieve()
                            .body(String.class);
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "调用千帆 v2 对话失败: " + e.getMessage());
        }

        return parseChatContent(raw);
    }

    /** 文档要求：Bearer 与 API Key 值拼接；若用户已带 Bearer 前缀则不再重复添加 */
    private static String authorizationHeader(String apiKey) {
        String k = apiKey.trim();
        if (k.length() >= 7 && "bearer ".equalsIgnoreCase(k.substring(0, 7))) {
            return k;
        }
        return "Bearer " + k;
    }

    private String parseChatContent(String raw) {
        try {
            JsonNode root = objectMapper.readTree(raw);
            if (root.has("error")) {
                JsonNode err = root.get("error");
                String msg = err.path("message").asText(err.toString());
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "千帆返回错误: " + msg);
            }
            JsonNode choice = root.path("choices").path(0).path("message").path("content");
            if (choice.isTextual()) {
                String t = choice.asText().trim();
                if (!t.isEmpty()) {
                    return t;
                }
            }
            if (root.has("result") && root.get("result").isTextual()) {
                return root.get("result").asText().trim();
            }
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "千帆返回格式异常，无 choices[0].message.content");
        } catch (ResponseStatusException e) {
            throw e;
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "解析千帆 v2 响应失败");
        }
    }
}
