package com.heath.community.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class FollowupRecord {
    private Long id;
    private Long taskId;
    private Long patientId;
    private Long doctorId;
    private LocalDate followupDate;
    private String followupType;
    private String symptoms;
    private String bloodPressure;
    private String bloodSugar;
    private BigDecimal weight;
    private String medicationCompliance;
    private String adverseReactions;
    private String lifestyleGuidance;
    private LocalDate nextFollowupDate;
    private String followupResult;
    private String remarks;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    
    private String patientName;
    private String doctorName;
    private String taskNo;
    private List<FollowupRecordMedicine> medicines;
}
