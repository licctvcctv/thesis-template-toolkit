package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class MedicalRecordMedicine {
    private Long id;
    private Long medicalRecordId;
    private Long medicineId;
    private Integer quantity;
    private String dosage;
    private LocalDateTime createTime;
    
    private String medicineName;
    private String medicineCode;
}
