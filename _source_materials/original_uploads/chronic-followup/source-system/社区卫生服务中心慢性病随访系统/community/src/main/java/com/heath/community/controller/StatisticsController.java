package com.heath.community.controller;

import com.heath.community.common.Result;
import com.heath.community.dto.StatisticsDTO;
import com.heath.community.service.StatisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/statistics")
@RequiredArgsConstructor
public class StatisticsController {
    private final StatisticsService statisticsService;

    @GetMapping
    public Result<StatisticsDTO> getStatistics() {
        return Result.success(statisticsService.getStatistics());
    }
}
