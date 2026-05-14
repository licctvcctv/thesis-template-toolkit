package com.heath.community.entity;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class FollowupTask {
    private Long id;
    private String taskNo;
    private Long patientId;
    private Long doctorId;
    private String taskType;
    private String taskContent;
    private LocalDate planDate;
    private LocalDate actualDate;
    private String status;
    private String priority;
    private Long creatorId;
    private LocalDate assignDate;
    private String remarks;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    
    private String patientName;
    private String doctorName;
    private String creatorName;
}
