package com.heath.community.dto;

import lombok.Data;

@Data
public class DoctorDTO {
    private Long id;
    private Long userId;
    private String username;
    private String name;
    private String employeeId;
    private String phone;
    private String email;
    private String department;
    private String title;
    private String specialty;
    private Integer status;
}
