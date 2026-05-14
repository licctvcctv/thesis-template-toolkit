package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class RiskLevelConfig {
    private Long id;
    private String levelCode;
    private String levelName;
    private String description;
    private Integer sortOrder;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
