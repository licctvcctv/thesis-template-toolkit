package com.heath.community.mapper;

import com.heath.community.entity.FollowupRecordMedicine;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface FollowupRecordMedicineMapper {
    List<FollowupRecordMedicine> findByRecordId(@Param("recordId") Long recordId);
    int insert(FollowupRecordMedicine medicine);
    int deleteByRecordId(@Param("recordId") Long recordId);
}
