package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class DoctorAssignment {
    private Long id;
    private Long patientId;
    private Long doctorId;
    private LocalDate assignDate;
    private Long assignerId;
    private Integer status;
    private String remarks;
    private LocalDateTime createTime;
    
    private String patientName;
    private String doctorName;
    private String assignerName;
}
