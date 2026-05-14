package com.heath.community.mapper;

import com.heath.community.entity.RiskLevelConfig;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface RiskLevelConfigMapper {
    List<RiskLevelConfig> findAllEnabled();
    RiskLevelConfig findByCode(@Param("code") String code);
    int insert(RiskLevelConfig config);
    int update(RiskLevelConfig config);
}
