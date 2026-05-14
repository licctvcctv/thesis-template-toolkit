package com.heath.community.dto;

import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
public class StatisticsDTO {
    // 患者统计
    private Long totalPatients;
    private Long patientsByDiseaseType;
    private Map<String, Long> patientsByDiseaseTypeMap;
    private Map<String, Long> patientsByRiskLevelMap;
    
    // 随访统计
    private Long totalFollowupTasks;
    private Long completedFollowupTasks;
    private Double followupCompletionRate;
    private Long totalFollowupRecords;
    private Double averageFollowupQuality;
    
    // 医生工作量统计
    private List<DoctorWorkloadDTO> doctorWorkloads;
}
