package com.heath.community.mapper;

import com.heath.community.entity.Patient;
import com.heath.community.dto.PatientDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface PatientMapper {
    List<PatientDTO> findPage(@Param("name") String name, @Param("patientNo") String patientNo,
                              @Param("diseaseType") String diseaseType, @Param("riskLevel") String riskLevel,
                              @Param("doctorId") Long doctorId, @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("name") String name, @Param("patientNo") String patientNo,
               @Param("diseaseType") String diseaseType, @Param("riskLevel") String riskLevel,
               @Param("doctorId") Long doctorId);
    PatientDTO findById(@Param("id") Long id);
    Patient findByPatientNo(@Param("patientNo") String patientNo);
    int insert(Patient patient);
    int update(Patient patient);
    int delete(@Param("id") Long id);
}
