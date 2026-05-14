package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.dto.PatientVitalSignsDTO;
import com.heath.community.entity.PatientVitalSigns;
import com.heath.community.service.PatientVitalSignsService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/patient-vital-signs")
@RequiredArgsConstructor
public class PatientVitalSignsController {
    private final PatientVitalSignsService patientVitalSignsService;

    @GetMapping("/page")
    public Result<PageResult<PatientVitalSignsDTO>> findPage(
            @RequestParam(required = false) Long patientId,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate,
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size) {
        return Result.success(patientVitalSignsService.findPage(patientId, startDate, endDate, page, size));
    }

    @GetMapping("/{id}")
    public Result<PatientVitalSignsDTO> findById(@PathVariable Long id) {
        return Result.success(patientVitalSignsService.findById(id));
    }

    @GetMapping("/patient/{patientId}")
    public Result<List<PatientVitalSignsDTO>> findByPatientId(
            @PathVariable Long patientId,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate) {
        return Result.success(patientVitalSignsService.findByPatientId(patientId, startDate, endDate));
    }

    @PostMapping
    public Result<Void> create(@RequestBody PatientVitalSigns vitalSigns) {
        patientVitalSignsService.create(vitalSigns);
        return Result.success();
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody PatientVitalSigns vitalSigns) {
        vitalSigns.setId(id);
        patientVitalSignsService.update(vitalSigns);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        patientVitalSignsService.delete(id);
        return Result.success();
    }
}
