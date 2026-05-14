package com.heath.community.dto;

import lombok.Data;
import java.time.LocalDate;

@Data
public class PatientDTO {
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
    private String doctorName;
    private String riskLevel;
    private String riskLevelName;
    private Integer status;
}
