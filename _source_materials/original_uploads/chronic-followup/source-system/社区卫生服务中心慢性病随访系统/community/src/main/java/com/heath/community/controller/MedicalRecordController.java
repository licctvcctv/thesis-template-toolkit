package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.dto.MedicalRecordDTO;
import com.heath.community.dto.MedicalRecordStatisticsDTO;
import com.heath.community.entity.MedicalRecord;
import com.heath.community.service.MedicalRecordService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/medical-record")
@RequiredArgsConstructor
public class MedicalRecordController {
    private final MedicalRecordService medicalRecordService;

    @GetMapping("/list")
    public Result<PageResult<MedicalRecordDTO>> list(@RequestParam(required = false) Long patientId,
                                                     @RequestParam(required = false) Long doctorId,
                                                     @RequestParam(required = false) String startDate,
                                                     @RequestParam(required = false) String endDate,
                                                     @RequestParam(defaultValue = "1") Long current,
                                                     @RequestParam(defaultValue = "10") Long size) {
        LocalDate start = startDate != null ? LocalDate.parse(startDate) : null;
        LocalDate end = endDate != null ? LocalDate.parse(endDate) : null;
        PageResult<MedicalRecordDTO> pageResult = medicalRecordService.findPage(patientId, doctorId, start, end, current, size);
        return Result.success(pageResult);
    }

    @GetMapping("/{id}")
    public Result<MedicalRecordDTO> getById(@PathVariable Long id) {
        MedicalRecordDTO record = medicalRecordService.findById(id);
        return Result.success(record);
    }

    @PostMapping("/add")
    public Result<Void> add(@RequestBody MedicalRecord record) {
        try {
            medicalRecordService.add(record);
            return Result.success("添加成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @PutMapping("/update")
    public Result<Void> update(@RequestBody MedicalRecord record) {
        try {
            medicalRecordService.update(record);
            return Result.success("更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        try {
            medicalRecordService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/statistics")
    public Result<MedicalRecordStatisticsDTO> statistics(@RequestParam(required = false) Long patientId,
                                                         @RequestParam(required = false) Long doctorId) {
        MedicalRecordStatisticsDTO statistics = medicalRecordService.getStatistics(patientId, doctorId);
        return Result.success(statistics);
    }
}
