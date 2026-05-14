package com.heath.community.mapper;

import com.heath.community.dto.PatientVitalSignsDTO;
import com.heath.community.entity.PatientVitalSigns;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface PatientVitalSignsMapper {
    List<PatientVitalSignsDTO> findPage(@Param("patientId") Long patientId,
                                        @Param("startDate") LocalDateTime startDate,
                                        @Param("endDate") LocalDateTime endDate,
                                        @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("patientId") Long patientId,
               @Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate);
    PatientVitalSignsDTO findById(@Param("id") Long id);
    List<PatientVitalSignsDTO> findByPatientId(@Param("patientId") Long patientId,
                                               @Param("startDate") LocalDateTime startDate,
                                               @Param("endDate") LocalDateTime endDate);
    int insert(PatientVitalSigns vitalSigns);
    int update(PatientVitalSigns vitalSigns);
    int delete(@Param("id") Long id);
}
