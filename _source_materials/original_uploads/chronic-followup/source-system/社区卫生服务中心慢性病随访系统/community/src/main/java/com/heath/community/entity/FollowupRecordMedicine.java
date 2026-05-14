package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class FollowupRecordMedicine {
    private Long id;
    private Long followupRecordId;
    private Long medicineId;
    private Integer quantity;
    private String dosage;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    
    private String medicineName;
    private String medicineCode;
}
