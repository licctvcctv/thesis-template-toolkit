package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.dto.FollowupRecordDTO;
import com.heath.community.dto.FollowupRecordMedicineDTO;
import com.heath.community.entity.FollowupRecord;
import com.heath.community.entity.FollowupRecordMedicine;
import com.heath.community.mapper.FollowupRecordMapper;
import com.heath.community.mapper.FollowupRecordMedicineMapper;
import com.heath.community.mapper.FollowupTaskMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FollowupRecordService {
    private final FollowupRecordMapper followupRecordMapper;
    private final FollowupRecordMedicineMapper followupRecordMedicineMapper;
    private final FollowupTaskMapper followupTaskMapper;

    public PageResult<FollowupRecordDTO> findPage(Long patientId, Long doctorId, Long taskId,
                                                  LocalDate startDate, LocalDate endDate, Integer page, Integer size) {
        Long offset = (long) (page - 1) * size;
        List<FollowupRecordDTO> list = followupRecordMapper.findPage(patientId, doctorId, taskId, startDate, endDate, offset, (long) size);
        
        for (FollowupRecordDTO record : list) {
            List<FollowupRecordMedicine> medicines = followupRecordMedicineMapper.findByRecordId(record.getId());
            record.setMedicines(medicines.stream().map(m -> {
                FollowupRecordMedicineDTO dto = new FollowupRecordMedicineDTO();
                dto.setId(m.getId());
                dto.setMedicineId(m.getMedicineId());
                dto.setMedicineName(m.getMedicineName());
                dto.setMedicineCode(m.getMedicineCode());
                dto.setQuantity(m.getQuantity());
                dto.setDosage(m.getDosage());
                return dto;
            }).collect(Collectors.toList()));
        }
        
        Long total = followupRecordMapper.count(patientId, doctorId, taskId, startDate, endDate);
        return PageResult.of(list, total, (long) page, (long) size);
    }

    public FollowupRecordDTO findById(Long id) {
        FollowupRecordDTO record = followupRecordMapper.findById(id);
        if (record != null) {
            List<FollowupRecordMedicine> medicines = followupRecordMedicineMapper.findByRecordId(id);
            record.setMedicines(medicines.stream().map(m -> {
                FollowupRecordMedicineDTO dto = new FollowupRecordMedicineDTO();
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
    public void create(FollowupRecord record) {
        followupRecordMapper.insert(record);
        
        if (record.getMedicines() != null && !record.getMedicines().isEmpty()) {
            for (FollowupRecordMedicine medicine : record.getMedicines()) {
                medicine.setFollowupRecordId(record.getId());
                followupRecordMedicineMapper.insert(medicine);
            }
        }
        
        if (record.getTaskId() != null) {
            followupTaskMapper.updateStatus(record.getTaskId(), "completed");
        }
    }

    @Transactional
    public void update(FollowupRecord record) {
        followupRecordMapper.update(record);
        
        followupRecordMedicineMapper.deleteByRecordId(record.getId());
        
        if (record.getMedicines() != null && !record.getMedicines().isEmpty()) {
            for (FollowupRecordMedicine medicine : record.getMedicines()) {
                medicine.setFollowupRecordId(record.getId());
                followupRecordMedicineMapper.insert(medicine);
            }
        }
    }

    @Transactional
    public void delete(Long id) {
        followupRecordMapper.delete(id);
    }
}
