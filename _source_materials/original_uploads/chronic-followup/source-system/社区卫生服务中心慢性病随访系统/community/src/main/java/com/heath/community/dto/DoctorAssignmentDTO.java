package com.heath.community.dto;

import lombok.Data;
import java.time.LocalDate;

@Data
public class DoctorAssignmentDTO {
    private Long id;
    private Long patientId;
    private String patientName;
    private Long doctorId;
    private String doctorName;
    private LocalDate assignDate;
    private Long assignerId;
    private String assignerName;
    private Integer status;
    private String remarks;
}
