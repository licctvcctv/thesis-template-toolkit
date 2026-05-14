package com.heath.community.mapper;

import com.heath.community.entity.MedicalRecordMedicine;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface MedicalRecordMedicineMapper {
    List<MedicalRecordMedicine> findByRecordId(@Param("recordId") Long recordId);
    int insert(MedicalRecordMedicine medicine);
    int deleteByRecordId(@Param("recordId") Long recordId);
}
