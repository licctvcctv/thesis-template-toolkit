package com.heath.community.mapper;

import com.heath.community.entity.DoctorAssignment;
import com.heath.community.dto.DoctorAssignmentDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface DoctorAssignmentMapper {
    List<DoctorAssignmentDTO> findPage(@Param("patientId") Long patientId, @Param("doctorId") Long doctorId,
                                      @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("patientId") Long patientId, @Param("doctorId") Long doctorId);
    DoctorAssignmentDTO findById(@Param("id") Long id);
    DoctorAssignment findCurrentAssignment(@Param("patientId") Long patientId);
    int insert(DoctorAssignment assignment);
    int updateStatus(@Param("patientId") Long patientId);
}
