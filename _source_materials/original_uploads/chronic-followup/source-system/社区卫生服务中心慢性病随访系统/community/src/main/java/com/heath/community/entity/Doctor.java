package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class Doctor {
    private Long id;
    private Long userId;
    private String employeeId;
    private String phone;
    private String email;
    private String department;
    private String title;
    private String specialty;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    
    private User user;
}
