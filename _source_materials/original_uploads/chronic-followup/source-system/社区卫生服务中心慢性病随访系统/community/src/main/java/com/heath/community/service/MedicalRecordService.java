package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.dto.MedicalRecordDTO;
import com.heath.community.dto.MedicalRecordMedicineDTO;
import com.heath.community.dto.MedicalRecordStatisticsDTO;
import com.heath.community.entity.MedicalRecord;
import com.heath.community.entity.MedicalRecordMedicine;
import com.heath.community.mapper.MedicalRecordMapper;
import com.heath.community.mapper.MedicalRecordMedicineMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class MedicalRecordService {
    private final MedicalRecordMapper medicalRecordMapper;
    private final MedicalRecordMedicineMapper medicalRecordMedicineMapper;

    public PageResult<MedicalRecordDTO> findPage(Long patientId, Long doctorId, LocalDate startDate,
                                                 LocalDate endDate, Long current, Long size) {
        Long offset = (current - 1) * size;
        List<MedicalRecordDTO> records = medicalRecordMapper.findPage(patientId, doctorId, startDate, endDate, offset, size);
        
        for (MedicalRecordDTO record : records) {
            List<MedicalRecordMedicine> medicines = medicalRecordMedicineMapper.findByRecordId(record.getId());
            record.setMedicines(medicines.stream().map(m -> {
                MedicalRecordMedicineDTO dto = new MedicalRecordMedicineDTO();
                dto.setId(m.getId());
                dto.setMedicineId(m.getMedicineId());
                dto.setMedicineName(m.getMedicineName());
                dto.setMedicineCode(m.getMedicineCode());
                dto.setQuantity(m.getQuantity());
                dto.setDosage(m.getDosage());
                return dto;
            }).collect(Collectors.toList()));
        }
        
        Long total = medicalRecordMapper.count(patientId, doctorId, startDate, endDate);
        return PageResult.of(records, total, current, size);
    }

    public MedicalRecordDTO findById(Long id) {
        MedicalRecordDTO record = medicalRecordMapper.findById(id);
        if (record != null) {
            List<MedicalRecordMedicine> medicines = medicalRecordMedicineMapper.findByRecordId(id);
            record.setMedicines(medicines.stream().map(m -> {
                MedicalRecordMedicineDTO dto = new MedicalRecordMedicineDTO();
                dto.setId(m.getId());
                dto.setMedicineId(m.getMedicineId());
                dto.setMedicineName(m.getMedicineName());
                dto.setMedicineCode(m.getMedicineCode());
                dto.setQuantity(m.getQuantity());
                dto.setDosage(m.getDosage());
                return dto;
            }).collect(Collectors.toList()));
        }
        return record;
    }

    @Transactional
    public void add(MedicalRecord record) {
        if (record.getRecordDate() == null) {
            record.setRecordDate(LocalDate.now());
        }
        medicalRecordMapper.insert(record);
        
        if (record.getMedicines() != null && !record.getMedicines().isEmpty()) {
            for (MedicalRecordMedicine medicine : record.getMedicines()) {
                medicine.setMedicalRecordId(record.getId());
                medicalRecordMedicineMapper.insert(medicine);
            }
        }
    }

    @Transactional
    public void update(MedicalRecord record) {
        MedicalRecordDTO existing = medicalRecordMapper.findById(record.getId());
        if (existing == null) {
            throw new RuntimeException("诊疗记录不存在");
        }
        
        medicalRecordMapper.update(record);
        
        medicalRecordMedicineMapper.deleteByRecordId(record.getId());
        
        if (record.getMedicines() != null && !record.getMedicines().isEmpty()) {
            for (MedicalRecordMedicine medicine : record.getMedicines()) {
                medicine.setMedicalRecordId(record.getId());
                medicalRecordMedicineMapper.insert(medicine);
            }
        }
    }

    @Transactional
    public void delete(Long id) {
        MedicalRecordDTO record = medicalRecordMapper.findById(id);
        if (record == null) {
            throw new RuntimeException("诊疗记录不存在");
        }
        medicalRecordMedicineMapper.deleteByRecordId(id);
        medicalRecordMapper.delete(id);
    }

    public MedicalRecordStatisticsDTO getStatistics(Long patientId, Long doctorId) {
        MedicalRecordStatisticsDTO statistics = new MedicalRecordStatisticsDTO();
        statistics.setTotalRecords(medicalRecordMapper.countTotal() != null ? medicalRecordMapper.countTotal() : 0L);
        statistics.setTodayRecords(medicalRecordMapper.countByDate(LocalDate.now()) != null ? medicalRecordMapper.countByDate(LocalDate.now()) : 0L);
        
        LocalDate now = LocalDate.now();
        Long monthCount = medicalRecordMapper.countByMonth(now.getYear(), now.getMonthValue());
        statistics.setThisMonthRecords(monthCount != null ? monthCount : 0L);
        
        if (patientId != null) {
            Long patientCount = medicalRecordMapper.countByPatient(patientId);
            statistics.setByPatientCount(patientCount != null ? patientCount : 0L);
        } else {
            statistics.setByPatientCount(0L);
        }
        
        if (doctorId != null) {
            Long doctorCount = medicalRecordMapper.countByDoctor(doctorId);
            statistics.setByDoctorCount(doctorCount != null ? doctorCount : 0L);
        } else {
            statistics.setByDoctorCount(0L);
        }
        
        return statistics;
    }
}
