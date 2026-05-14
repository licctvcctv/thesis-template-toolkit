package com.heath.community.mapper;

import com.heath.community.dto.FollowupTaskDTO;
import com.heath.community.entity.FollowupTask;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDate;
import java.util.List;

@Mapper
public interface FollowupTaskMapper {
    List<FollowupTaskDTO> findPage(@Param("patientId") Long patientId, @Param("doctorId") Long doctorId,
                                   @Param("status") String status, @Param("startDate") LocalDate startDate,
                                   @Param("endDate") LocalDate endDate, @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("patientId") Long patientId, @Param("doctorId") Long doctorId,
              @Param("status") String status, @Param("startDate") LocalDate startDate, @Param("endDate") LocalDate endDate);
    FollowupTaskDTO findById(@Param("id") Long id);
    FollowupTask findByTaskNo(@Param("taskNo") String taskNo);
    int insert(FollowupTask task);
    int update(FollowupTask task);
    int delete(@Param("id") Long id);
    int updateStatus(@Param("id") Long id, @Param("status") String status);
    Long countByStatus(@Param("status") String status);
    Long countByDoctorAndStatus(@Param("doctorId") Long doctorId, @Param("status") String status);
}
