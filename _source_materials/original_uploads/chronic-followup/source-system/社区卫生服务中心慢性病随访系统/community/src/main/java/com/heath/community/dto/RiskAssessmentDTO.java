package com.heath.community.dto;

import lombok.Data;
import java.time.LocalDate;

@Data
public class RiskAssessmentDTO {
    private Long id;
    private Long patientId;
    private String patientName;
    private String riskLevel;
    private String riskLevelName;
    private LocalDate assessmentDate;
    private Long assessorId;
    private String assessorName;
    private String assessmentResult;
    private String remarks;
}
