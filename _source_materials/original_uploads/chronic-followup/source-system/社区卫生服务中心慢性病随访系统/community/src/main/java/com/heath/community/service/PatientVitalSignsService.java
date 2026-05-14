package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.dto.PatientVitalSignsDTO;
import com.heath.community.entity.PatientVitalSigns;
import com.heath.community.mapper.PatientVitalSignsMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class PatientVitalSignsService {
    private final PatientVitalSignsMapper patientVitalSignsMapper;

    public PageResult<PatientVitalSignsDTO> findPage(Long patientId, LocalDateTime startDate,
                                                     LocalDateTime endDate, Integer page, Integer size) {
        Long offset = (long) (page - 1) * size;
        List<PatientVitalSignsDTO> list = patientVitalSignsMapper.findPage(patientId, startDate, endDate, offset, (long) size);
        Long total = patientVitalSignsMapper.count(patientId, startDate, endDate);
        return PageResult.of(list, total, (long) page, (long) size);
    }

    public PatientVitalSignsDTO findById(Long id) {
        return patientVitalSignsMapper.findById(id);
    }

    public List<PatientVitalSignsDTO> findByPatientId(Long patientId, LocalDateTime startDate, LocalDateTime endDate) {
        return patientVitalSignsMapper.findByPatientId(patientId, startDate, endDate);
    }

    @Transactional
    public void create(PatientVitalSigns vitalSigns) {
        patientVitalSignsMapper.insert(vitalSigns);
    }

    @Transactional
    public void update(PatientVitalSigns vitalSigns) {
        patientVitalSignsMapper.update(vitalSigns);
    }

    @Transactional
    public void delete(Long id) {
        patientVitalSignsMapper.delete(id);
    }
}
