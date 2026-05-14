package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class MedicalRecord {
    private Long id;
    private Long patientId;
    private Long doctorId;
    private LocalDate recordDate;
    private String chiefComplaint;
    private String presentIllness;
    private String physicalExamination;
    private String diagnosis;
    private String treatmentPlan;
    private String medication;
    private String remarks;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    
    private String patientName;
    private String doctorName;
    private List<MedicalRecordMedicine> medicines;
}
