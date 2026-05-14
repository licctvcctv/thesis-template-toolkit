package com.heath.community.dto;

import lombok.Data;
import java.time.LocalDate;
import java.util.List;

@Data
public class MedicalRecordDTO {
    private Long id;
    private Long patientId;
    private String patientName;
    private Long doctorId;
    private String doctorName;
    private LocalDate recordDate;
    private String chiefComplaint;
    private String presentIllness;
    private String physicalExamination;
    private String diagnosis;
    private String treatmentPlan;
    private String medication;
    private String remarks;
    private List<MedicalRecordMedicineDTO> medicines;
}
