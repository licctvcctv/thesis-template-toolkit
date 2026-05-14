package com.heath.community.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class PatientVitalSignsDTO {
    private Long id;
    private Long patientId;
    private String patientName;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime recordDate;
    private Integer bloodPressureSystolic;
    private Integer bloodPressureDiastolic;
    private String bloodPressure;
    private BigDecimal bloodSugar;
    private String bloodSugarType;
    private String bloodSugarTypeName;
    private String remarks;
}
