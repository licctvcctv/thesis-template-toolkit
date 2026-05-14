package com.heath.community.mapper;

import com.heath.community.dto.FollowupRecordDTO;
import com.heath.community.entity.FollowupRecord;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDate;
import java.util.List;

@Mapper
public interface FollowupRecordMapper {
    List<FollowupRecordDTO> findPage(@Param("patientId") Long patientId, @Param("doctorId") Long doctorId,
                                    @Param("taskId") Long taskId, @Param("startDate") LocalDate startDate,
                                    @Param("endDate") LocalDate endDate, @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("patientId") Long patientId, @Param("doctorId") Long doctorId,
              @Param("taskId") Long taskId, @Param("startDate") LocalDate startDate, @Param("endDate") LocalDate endDate);
    FollowupRecordDTO findById(@Param("id") Long id);
    int insert(FollowupRecord record);
    int update(FollowupRecord record);
    int delete(@Param("id") Long id);
}
