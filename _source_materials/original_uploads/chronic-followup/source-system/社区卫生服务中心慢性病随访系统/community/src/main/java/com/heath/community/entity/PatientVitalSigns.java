package com.heath.community.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class PatientVitalSigns {
    private Long id;
    private Long patientId;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime recordDate;
    private Integer bloodPressureSystolic;
    private Integer bloodPressureDiastolic;
    private BigDecimal bloodSugar;
    private String bloodSugarType;
    private String remarks;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    
    private String patientName;
}
