package com.heath.community.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Data
public class FollowupRecordDTO {
    private Long id;
    private Long taskId;
    private String taskNo;
    private Long patientId;
    private String patientName;
    private Long doctorId;
    private String doctorName;
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
    private List<FollowupRecordMedicineDTO> medicines;
}
