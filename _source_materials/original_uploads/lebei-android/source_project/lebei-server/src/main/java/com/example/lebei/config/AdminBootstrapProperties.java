package com.example.lebei.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "lebei.admin")
public class AdminBootstrapProperties {

    /** 首个管理员用户名（仅当库中尚无任何管理员时自动创建） */
    private String username = "admin";

    /** 初始登录密码，部署后请在数据库或管理流程中修改 */
    private String initialPassword = "Admin123456!";

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getInitialPassword() {
        return initialPassword;
    }

    public void setInitialPassword(String initialPassword) {
        this.initialPassword = initialPassword;
    }
}
