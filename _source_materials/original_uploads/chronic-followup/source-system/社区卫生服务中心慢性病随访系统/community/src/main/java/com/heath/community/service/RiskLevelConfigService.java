package com.heath.community.service;

import com.heath.community.entity.RiskLevelConfig;
import com.heath.community.mapper.RiskLevelConfigMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class RiskLevelConfigService {
    private final RiskLevelConfigMapper riskLevelConfigMapper;

    public List<RiskLevelConfig> findAllEnabled() {
        return riskLevelConfigMapper.findAllEnabled();
    }

    public RiskLevelConfig findByCode(String code) {
        return riskLevelConfigMapper.findByCode(code);
    }

    public void add(RiskLevelConfig config) {
        RiskLevelConfig existing = riskLevelConfigMapper.findByCode(config.getLevelCode());
        if (existing != null) {
            throw new RuntimeException("风险等级代码已存在");
        }
        if (config.getStatus() == null) {
            config.setStatus(1);
        }
        riskLevelConfigMapper.insert(config);
    }

    public void update(RiskLevelConfig config) {
        RiskLevelConfig existing = riskLevelConfigMapper.findByCode(config.getLevelCode());
        if (existing == null) {
            throw new RuntimeException("风险等级配置不存在");
        }
        config.setId(existing.getId());
        riskLevelConfigMapper.update(config);
    }
}
