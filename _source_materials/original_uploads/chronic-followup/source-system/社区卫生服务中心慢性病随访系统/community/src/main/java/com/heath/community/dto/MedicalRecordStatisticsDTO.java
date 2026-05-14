package com.heath.community.dto;

import lombok.Data;

@Data
public class MedicalRecordStatisticsDTO {
    private Long totalRecords;
    private Long todayRecords;
    private Long thisMonthRecords;
    private Long byPatientCount;
    private Long byDoctorCount;
}
