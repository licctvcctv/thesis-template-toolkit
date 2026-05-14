package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.entity.Medicine;
import com.heath.community.mapper.MedicineMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MedicineService {
    private final MedicineMapper medicineMapper;

    public PageResult<Medicine> findPage(String medicineName, String medicineCode, Long current, Long size) {
        Long offset = (current - 1) * size;
        List<Medicine> records = medicineMapper.findPage(medicineName, medicineCode, offset, size);
        Long total = medicineMapper.count(medicineName, medicineCode);
        return PageResult.of(records, total, current, size);
    }

    public Medicine findById(Long id) {
        return medicineMapper.findById(id);
    }

    @Transactional
    public void add(Medicine medicine) {
        if (medicine.getMedicineCode() == null || medicine.getMedicineCode().isEmpty()) {
            throw new RuntimeException("药品编码不能为空");
        }
        
        Medicine existing = medicineMapper.findByCode(medicine.getMedicineCode());
        if (existing != null) {
            throw new RuntimeException("药品编码已存在");
        }
        
        if (medicine.getMedicineName() == null || medicine.getMedicineName().isEmpty()) {
            throw new RuntimeException("药品名称不能为空");
        }
        
        if (medicine.getStatus() == null) {
            medicine.setStatus(1);
        }
        
        if (medicine.getStock() == null) {
            medicine.setStock(0);
        }
        
        medicineMapper.insert(medicine);
    }

    @Transactional
    public void update(Medicine medicine) {
        Medicine existing = medicineMapper.findById(medicine.getId());
        if (existing == null) {
            throw new RuntimeException("药品不存在");
        }
        
        if (medicine.getMedicineCode() != null && !medicine.getMedicineCode().equals(existing.getMedicineCode())) {
            Medicine duplicate = medicineMapper.findByCode(medicine.getMedicineCode());
            if (duplicate != null && !duplicate.getId().equals(medicine.getId())) {
                throw new RuntimeException("药品编码已存在");
            }
        }
        
        medicineMapper.update(medicine);
    }

    @Transactional
    public void delete(Long id) {
        Medicine medicine = medicineMapper.findById(id);
        if (medicine == null) {
            throw new RuntimeException("药品不存在");
        }
        medicineMapper.delete(id);
    }
}
