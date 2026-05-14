package com.heath.community.mapper;

import com.heath.community.dto.MedicalRecordDTO;
import com.heath.community.entity.MedicalRecord;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDate;
import java.util.List;

@Mapper
public interface MedicalRecordMapper {
    List<MedicalRecordDTO> findPage(@Param("patientId") Long patientId, @Param("doctorId") Long doctorId,
                                    @Param("startDate") LocalDate startDate, @Param("endDate") LocalDate endDate,
                                    @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("patientId") Long patientId, @Param("doctorId") Long doctorId,
              @Param("startDate") LocalDate startDate, @Param("endDate") LocalDate endDate);
    MedicalRecordDTO findById(@Param("id") Long id);
    int insert(MedicalRecord record);
    int update(MedicalRecord record);
    int delete(@Param("id") Long id);
    Long countTotal();
    Long countByDate(@Param("date") LocalDate date);
    Long countByMonth(@Param("year") Integer year, @Param("month") Integer month);
    Long countByPatient(@Param("patientId") Long patientId);
    Long countByDoctor(@Param("doctorId") Long doctorId);
}
