package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.dto.RiskAssessmentDTO;
import com.heath.community.entity.RiskAssessment;
import com.heath.community.service.RiskAssessmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/risk-assessment")
@RequiredArgsConstructor
public class RiskAssessmentController {
    private final RiskAssessmentService riskAssessmentService;

    @GetMapping("/list")
    public Result<PageResult<RiskAssessmentDTO>> list(@RequestParam(required = false) Long patientId,
                                                      @RequestParam(required = false) String riskLevel,
                                                      @RequestParam(defaultValue = "1") Long current,
                                                      @RequestParam(defaultValue = "10") Long size) {
        PageResult<RiskAssessmentDTO> pageResult = riskAssessmentService.findPage(patientId, riskLevel, current, size);
        return Result.success(pageResult);
    }

    @GetMapping("/{id}")
    public Result<RiskAssessmentDTO> getById(@PathVariable Long id) {
        RiskAssessmentDTO assessment = riskAssessmentService.findById(id);
        return Result.success(assessment);
    }

    @PostMapping("/add")
    public Result<Void> add(@RequestBody RiskAssessment assessment) {
        try {
            riskAssessmentService.add(assessment);
            return Result.success("评估成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
