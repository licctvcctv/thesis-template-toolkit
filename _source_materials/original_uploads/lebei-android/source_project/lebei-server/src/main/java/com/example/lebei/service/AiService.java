package com.example.lebei.service;

import com.example.lebei.config.AiProperties;
import com.example.lebei.dto.ai.AiEssayWordItem;
import com.example.lebei.entity.UserEntity;
import com.example.lebei.repository.UserRepository;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

/** 使用百度千帆文心大模型生成例句与短文，难度依据用户在库中的 level / ageGroup。 */
@Service
public class AiService {

    private final AiProperties aiProperties;
    private final UserRepository userRepository;
    private final QianfanChatService qianfanChat;

    public AiService(AiProperties aiProperties, UserRepository userRepository, QianfanChatService qianfanChat) {
        this.aiProperties = aiProperties;
        this.userRepository = userRepository;
        this.qianfanChat = qianfanChat;
    }

    @Transactional(readOnly = true)
    public String generateExample(Long userId, String word, String phonetic, String translation) {
        requireQianfanConfigured();
        UserEntity user =
                userRepository.findById(userId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        String levelHint = buildLevelHint(user);

        String userPrompt =
                "单词: "
                        + word
                        + "\n音标: "
                        + (phonetic != null ? phonetic : "")
                        + "\n中文释义: "
                        + translation
                        + "\n\n请输出：\n1) 一行地道的英文例句（必须自然包含该词或其常见词形变化）。\n2) 下一行用中文一句话解释该英文例句的意思。\n不要输出其它标题或多余说明。";

        String system =
                "你是面向中国学生的英语教师。"
                        + levelHint
                        + " 例句难度、长度和用词必须严格匹配该水平，不要超纲。";

        return qianfanChat.chat(system, userPrompt);
    }

    @Transactional(readOnly = true)
    public String generateEssay(Long userId, List<AiEssayWordItem> words) {
        requireQianfanConfigured();
        UserEntity user =
                userRepository.findById(userId).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
        String levelHint = buildLevelHint(user);

        String list =
                words.stream()
                        .map(w -> "- " + w.getWord() + " : " + w.getTranslation())
                        .collect(Collectors.joining("\n"));

        String userPrompt =
                "今日要融入短文的单词列表（英文 + 中文释义）：\n"
                        + list
                        + "\n\n请写一段连贯的英文短文（约 90～160 个英文词），尽量自然覆盖其中多数词汇，不必生硬堆砌每一个词。"
                        + "短文后空一行，写一行「中文大意：」开头，用 1～2 句中文概括全文。"
                        + "若学习者标注为儿童，可写带简单对话的童趣小故事，仍以英文正文为主。";

        String system =
                "你是面向中国学生的英语教师，根据学习者英语水平组织语言和句式。"
                        + levelHint
                        + " 词汇与句式难度必须与该水平一致。";

        return qianfanChat.chat(system, userPrompt);
    }

    private void requireQianfanConfigured() {
        String problem = aiProperties.describeQianfanKeyMisconfiguration();
        if (problem != null) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, problem);
        }
    }

    private String buildLevelHint(UserEntity user) {
        String level = user.getLevel() != null ? user.getLevel().toLowerCase() : "cet4";
        Integer age = user.getAgeGroup();
        String base =
                switch (level) {
                    case "junior" -> "学习者水平：中国初中英语，句子要短、词汇简单常见。";
                    case "senior" -> "学习者水平：中国高中英语，可适当使用从句，避免过难学术词汇。";
                    case "cet4" -> "学习者水平：大学英语四级，语言自然准确，题材贴近校园与日常。";
                    case "cet6" -> "学习者水平：大学英语六级，可使用稍复杂结构与书面表达，仍要清晰易懂。";
                    default -> "学习者水平：中等，难度介于高中与四级之间。";
                };
        if (age != null && age == 1) {
            base += " 年龄段：儿童，语气亲切，句子更短，避免抽象概念。";
        } else if (age != null && age == 2) {
            base += " 年龄段：青少年，可略活泼，仍要规范英语。";
        }
        return base;
    }
}
