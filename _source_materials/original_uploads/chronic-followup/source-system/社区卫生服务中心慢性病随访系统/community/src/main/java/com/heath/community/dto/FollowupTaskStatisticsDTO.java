package com.heath.community.dto;

import lombok.Data;

@Data
public class FollowupTaskStatisticsDTO {
    private Long totalTasks;
    private Long pendingTasks;
    private Long completedTasks;
    private Long inProgressTasks;
    private Double completionRate;
}
