package com.heath.community.dto;

import lombok.Data;

@Data
public class FollowupRecordMedicineDTO {
    private Long id;
    private Long medicineId;
    private String medicineName;
    private String medicineCode;
    private Integer quantity;
    private String dosage;
}
