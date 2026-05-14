package com.heath.community.dto;

import lombok.Data;
import java.time.LocalDate;

@Data
public class FollowupTaskDTO {
    private Long id;
    private String taskNo;
    private Long patientId;
    private String patientName;
    private Long doctorId;
    private String doctorName;
    private String taskType;
    private String taskContent;
    private LocalDate planDate;
    private LocalDate actualDate;
    private String status;
    private String statusName;
    private String priority;
    private String priorityName;
    private Long creatorId;
    private String creatorName;
    private LocalDate assignDate;
    private String remarks;
}
