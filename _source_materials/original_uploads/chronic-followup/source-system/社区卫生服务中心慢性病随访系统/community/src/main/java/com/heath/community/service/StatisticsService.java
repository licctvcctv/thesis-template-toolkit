package com.heath.community.service;

import com.heath.community.dto.StatisticsDTO;
import com.heath.community.dto.DoctorWorkloadDTO;
import com.heath.community.mapper.PatientMapper;
import com.heath.community.mapper.FollowupTaskMapper;
import com.heath.community.mapper.FollowupRecordMapper;
import com.heath.community.mapper.MedicalRecordMapper;
import com.heath.community.mapper.DoctorMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class StatisticsService {
    private final PatientMapper patientMapper;
    private final FollowupTaskMapper followupTaskMapper;
    private final FollowupRecordMapper followupRecordMapper;
    private final MedicalRecordMapper medicalRecordMapper;
    private final DoctorMapper doctorMapper;

    public StatisticsDTO getStatistics() {
        StatisticsDTO stats = new StatisticsDTO();
        
        // 患者总数（仅用于显示统计卡片）
        stats.setTotalPatients(patientMapper.count(null, null, null, null, null));
        
        // 随访统计
        stats.setTotalFollowupTasks(followupTaskMapper.count(null, null, null, null, null));
        stats.setCompletedFollowupTasks(followupTaskMapper.countByStatus("completed"));
        if (stats.getTotalFollowupTasks() > 0) {
            stats.setFollowupCompletionRate((double) stats.getCompletedFollowupTasks() / stats.getTotalFollowupTasks() * 100);
        } else {
            stats.setFollowupCompletionRate(0.0);
        }
        stats.setTotalFollowupRecords(followupRecordMapper.count(null, null, null, null, null));
        
        // 医生工作量统计
        List<com.heath.community.dto.DoctorDTO> doctors = doctorMapper.findPage(null, null, null, 0L, 10000L);
        List<DoctorWorkloadDTO> workloads = new ArrayList<>();
        for (com.heath.community.dto.DoctorDTO doctor : doctors) {
            DoctorWorkloadDTO workload = new DoctorWorkloadDTO();
            workload.setDoctorId(doctor.getId());
            workload.setDoctorName(doctor.getName());
            workload.setPatientCount(patientMapper.count(null, null, null, null, doctor.getId()));
            workload.setFollowupTaskCount(followupTaskMapper.count(null, doctor.getId(), null, null, null));
            workload.setFollowupRecordCount(followupRecordMapper.count(null, doctor.getId(), null, null, null));
            workload.setMedicalRecordCount(medicalRecordMapper.countByDoctor(doctor.getId()));
            workloads.add(workload);
        }
        stats.setDoctorWorkloads(workloads);
        
        return stats;
    }
}
