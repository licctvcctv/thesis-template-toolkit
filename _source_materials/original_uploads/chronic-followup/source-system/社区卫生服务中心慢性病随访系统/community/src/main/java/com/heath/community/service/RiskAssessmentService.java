package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.dto.PatientDTO;
import com.heath.community.dto.RiskAssessmentDTO;
import com.heath.community.entity.Patient;
import com.heath.community.entity.RiskAssessment;
import com.heath.community.mapper.PatientMapper;
import com.heath.community.mapper.RiskAssessmentMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class RiskAssessmentService {
    private final RiskAssessmentMapper riskAssessmentMapper;
    private final PatientMapper patientMapper;

    public PageResult<RiskAssessmentDTO> findPage(Long patientId, String riskLevel, Long current, Long size) {
        Long offset = (current - 1) * size;
        var records = riskAssessmentMapper.findPage(patientId, riskLevel, offset, size);
        Long total = riskAssessmentMapper.count(patientId, riskLevel);
        return PageResult.of(records, total, current, size);
    }

    public RiskAssessmentDTO findById(Long id) {
        return riskAssessmentMapper.findById(id);
    }

    @Transactional
    public void add(RiskAssessment assessment) {
        PatientDTO patientDTO = patientMapper.findById(assessment.getPatientId());
        if (patientDTO == null) {
            throw new RuntimeException("患者不存在");
        }
        
        riskAssessmentMapper.insert(assessment);
        
        Patient patientUpdate = new Patient();
        patientUpdate.setId(assessment.getPatientId());
        patientUpdate.setRiskLevel(assessment.getRiskLevel());
        patientMapper.update(patientUpdate);
    }
}
