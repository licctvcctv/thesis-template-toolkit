package com.example.lebei.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * 千帆 v2 对话接口：使用「安全认证 - API Key」中的整串密钥（通常以 bce-v3/ALTAK- 开头），
 * 不再使用应用内的旧版 API Key + Secret Key 换 token。
 */
@Component
@ConfigurationProperties(prefix = "lebei.ai")
public class AiProperties {

    /**
     * 控制台「安全认证 - API Key」创建的密钥整串；或环境变量 QIANFAN_API_KEY。
     * 请求头格式：Authorization: Bearer &lt;本值&gt;
     */
    private String qianfanApiKey = "";

    /**
     * 模型 ID，与官方「文本生成」文档中 model 入参一致，例如 ernie-3.5-8k、ernie-speed-8k（以控制台已开通为准）
     */
    private String qianfanModel = "ernie-3.5-8k";

    public String effectiveQianfanApiKey() {
        String env = System.getenv("QIANFAN_API_KEY");
        if (env != null && !env.isBlank()) {
            return env.trim();
        }
        if (qianfanApiKey != null && !qianfanApiKey.isBlank()) {
            return qianfanApiKey.trim();
        }
        return "";
    }

    /**
     * @return 若可继续调用千帆则 null；否则返回面向运维/用户的中文说明（应映射为 503）
     */
    public String describeQianfanKeyMisconfiguration() {
        String raw = effectiveQianfanApiKey();
        if (raw.isBlank()) {
            return "未配置千帆 v2 API Key：请设置环境变量 QIANFAN_API_KEY，或在 application-secrets.yml 填写 qianfan-api-key（IAM 控制台复制的整串密钥）后重启。说明见 application-secrets.example.yml";
        }
        String material = raw;
        if (material.length() >= 7 && material.regionMatches(true, 0, "Bearer ", 0, 7)) {
            material = material.substring(7).trim();
        }
        if (material.chars().anyMatch(cp -> cp > 0x7F)) {
            return "千帆 API Key 不能含中文或其它非 ASCII 字符，否则会报 invalid header value。"
                    + "请到 https://console.bce.baidu.com/iam/#/iam/apikey/list 复制整串密钥（形如 bce-v3/ALTAK-...，仅英文、数字、/、-、_ 等），替换 qianfan-api-key 或 QIANFAN_API_KEY 后重启。";
        }
        if (material.contains("在这里粘贴")
                || material.toLowerCase().contains("paste your")
                || material.toLowerCase().contains("your-api-key")
                || material.toUpperCase().contains("REPLACE_WITH")) {
            return "检测到 qianfan-api-key 仍是说明文档里的占位文字，不是真实密钥。请到 IAM 控制台创建并复制整串 API Key（一般为 bce-v3/ALTAK-...）写入配置后重启。";
        }
        return null;
    }

    public String getQianfanApiKey() {
        return qianfanApiKey;
    }

    public void setQianfanApiKey(String qianfanApiKey) {
        this.qianfanApiKey = qianfanApiKey;
    }

    public String getQianfanModel() {
        return qianfanModel;
    }

    public void setQianfanModel(String qianfanModel) {
        this.qianfanModel = qianfanModel;
    }
}
