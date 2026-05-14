package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class RiskAssessment {
    private Long id;
    private Long patientId;
    private String riskLevel;
    private LocalDate assessmentDate;
    private Long assessorId;
    private String assessmentResult;
    private String remarks;
    private LocalDateTime createTime;
    
    private String patientName;
    private String assessorName;
    private String riskLevelName;
}
