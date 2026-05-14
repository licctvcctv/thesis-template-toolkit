package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.dto.DoctorAssignmentDTO;
import com.heath.community.dto.PatientDTO;
import com.heath.community.entity.DoctorAssignment;
import com.heath.community.entity.Patient;
import com.heath.community.mapper.DoctorAssignmentMapper;
import com.heath.community.mapper.PatientMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class DoctorAssignmentService {
    private final DoctorAssignmentMapper doctorAssignmentMapper;
    private final PatientMapper patientMapper;

    public PageResult<DoctorAssignmentDTO> findPage(Long patientId, Long doctorId, Long current, Long size) {
        Long offset = (current - 1) * size;
        var records = doctorAssignmentMapper.findPage(patientId, doctorId, offset, size);
        Long total = doctorAssignmentMapper.count(patientId, doctorId);
        return PageResult.of(records, total, current, size);
    }

    public DoctorAssignmentDTO findById(Long id) {
        return doctorAssignmentMapper.findById(id);
    }

    @Transactional
    public void assign(Long patientId, Long doctorId, Long assignerId, String remarks) {
        PatientDTO patient = patientMapper.findById(patientId);
        if (patient == null) {
            throw new RuntimeException("患者不存在");
        }
        
        doctorAssignmentMapper.updateStatus(patientId);
        
        DoctorAssignment assignment = new DoctorAssignment();
        assignment.setPatientId(patientId);
        assignment.setDoctorId(doctorId);
        assignment.setAssignDate(LocalDate.now());
        assignment.setAssignerId(assignerId);
        assignment.setStatus(1);
        assignment.setRemarks(remarks);
        doctorAssignmentMapper.insert(assignment);
        
        Patient patientUpdate = new Patient();
        patientUpdate.setId(patientId);
        patientUpdate.setCurrentDoctorId(doctorId);
        patientMapper.update(patientUpdate);
    }
}
