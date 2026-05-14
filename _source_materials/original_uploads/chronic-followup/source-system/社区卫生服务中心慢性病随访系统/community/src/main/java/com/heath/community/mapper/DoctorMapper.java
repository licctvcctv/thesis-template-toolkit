package com.heath.community.mapper;

import com.heath.community.entity.Doctor;
import com.heath.community.dto.DoctorDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface DoctorMapper {
    List<DoctorDTO> findPage(@Param("name") String name, @Param("employeeId") String employeeId, 
                             @Param("department") String department, @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("name") String name, @Param("employeeId") String employeeId, @Param("department") String department);
    DoctorDTO findById(@Param("id") Long id);
    Doctor findByUserId(@Param("userId") Long userId);
    int insert(Doctor doctor);
    int update(Doctor doctor);
    int delete(@Param("id") Long id);
}
