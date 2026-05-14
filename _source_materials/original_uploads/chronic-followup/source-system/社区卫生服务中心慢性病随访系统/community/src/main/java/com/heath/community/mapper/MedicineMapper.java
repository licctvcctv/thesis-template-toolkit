package com.heath.community.mapper;

import com.heath.community.entity.Medicine;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface MedicineMapper {
    List<Medicine> findPage(@Param("medicineName") String medicineName, @Param("medicineCode") String medicineCode,
                            @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("medicineName") String medicineName, @Param("medicineCode") String medicineCode);
    Medicine findById(@Param("id") Long id);
    Medicine findByCode(@Param("code") String code);
    int insert(Medicine medicine);
    int update(Medicine medicine);
    int delete(@Param("id") Long id);
}
