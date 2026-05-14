package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class Patient {
    private Long id;
    private String patientNo;
    private String name;
    private Integer gender;
    private LocalDate birthday;
    private String idCard;
    private String phone;
    private String address;
    private String diseaseType;
    private LocalDate diagnosisDate;
    private Long currentDoctorId;
    private String riskLevel;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    
    private String doctorName;
}
