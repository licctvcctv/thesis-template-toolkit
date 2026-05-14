package com.heath.community.dto;

import lombok.Data;

@Data
public class DoctorWorkloadDTO {
    private Long doctorId;
    private String doctorName;
    private Long patientCount;
    private Long followupTaskCount;
    private Long followupRecordCount;
    private Long medicalRecordCount;
}
