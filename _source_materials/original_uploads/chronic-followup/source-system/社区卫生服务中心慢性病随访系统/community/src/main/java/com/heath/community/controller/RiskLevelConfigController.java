package com.heath.community.controller;

import com.heath.community.common.Result;
import com.heath.community.entity.RiskLevelConfig;
import com.heath.community.service.RiskLevelConfigService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/risk-level-config")
@RequiredArgsConstructor
public class RiskLevelConfigController {
    private final RiskLevelConfigService riskLevelConfigService;

    @GetMapping("/enabled")
    public Result<List<RiskLevelConfig>> listEnabled() {
        List<RiskLevelConfig> list = riskLevelConfigService.findAllEnabled();
        return Result.success(list);
    }

    @PostMapping("/add")
    public Result<Void> add(@RequestBody RiskLevelConfig config) {
        try {
            riskLevelConfigService.add(config);
            return Result.success("添加成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @PutMapping("/update")
    public Result<Void> update(@RequestBody RiskLevelConfig config) {
        try {
            riskLevelConfigService.update(config);
            return Result.success("更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
