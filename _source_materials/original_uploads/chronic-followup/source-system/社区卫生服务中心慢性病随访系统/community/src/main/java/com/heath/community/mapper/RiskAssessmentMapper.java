package com.heath.community.mapper;

import com.heath.community.entity.RiskAssessment;
import com.heath.community.dto.RiskAssessmentDTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface RiskAssessmentMapper {
    List<RiskAssessmentDTO> findPage(@Param("patientId") Long patientId, @Param("riskLevel") String riskLevel,
                                     @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("patientId") Long patientId, @Param("riskLevel") String riskLevel);
    RiskAssessmentDTO findById(@Param("id") Long id);
    int insert(RiskAssessment assessment);
}
