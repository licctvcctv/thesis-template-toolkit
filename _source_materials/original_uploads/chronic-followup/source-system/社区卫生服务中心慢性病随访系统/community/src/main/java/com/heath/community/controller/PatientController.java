package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.dto.PatientDTO;
import com.heath.community.entity.Patient;
import com.heath.community.service.PatientService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import jakarta.servlet.http.HttpServletResponse;

@RestController
@RequestMapping("/api/patient")
@RequiredArgsConstructor
public class PatientController {
    private final PatientService patientService;

    @GetMapping("/list")
    public Result<PageResult<PatientDTO>> list(@RequestParam(required = false) String name,
                                                @RequestParam(required = false) String patientNo,
                                                @RequestParam(required = false) String diseaseType,
                                                @RequestParam(required = false) String riskLevel,
                                                @RequestParam(required = false) Long doctorId,
                                                @RequestParam(defaultValue = "1") Long current,
                                                @RequestParam(defaultValue = "10") Long size) {
        PageResult<PatientDTO> pageResult = patientService.findPage(name, patientNo, diseaseType, riskLevel, doctorId, current, size);
        return Result.success(pageResult);
    }

    @GetMapping("/{id}")
    public Result<PatientDTO> getById(@PathVariable Long id) {
        PatientDTO patient = patientService.findById(id);
        return Result.success(patient);
    }

    @PostMapping("/add")
    public Result<Void> add(@RequestBody Patient patient) {
        try {
            patientService.add(patient);
            return Result.success("添加成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @PutMapping("/update")
    public Result<Void> update(@RequestBody Patient patient) {
        try {
            patientService.update(patient);
            return Result.success("更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        try {
            patientService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/export")
    public void export(@RequestParam(required = false) String name,
                      @RequestParam(required = false) String patientNo,
                      @RequestParam(required = false) String diseaseType,
                      @RequestParam(required = false) String riskLevel,
                      HttpServletResponse response) {
        try {
            patientService.export(name, patientNo, diseaseType, riskLevel, response);
        } catch (Exception e) {
            throw new RuntimeException("导出失败：" + e.getMessage());
        }
    }

    @PostMapping("/import")
    public Result<String> importData(@RequestParam("file") MultipartFile file) {
        try {
            int count = patientService.importData(file);
            return Result.success("导入成功，共导入 " + count + " 条数据", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        } catch (Exception e) {
            return Result.error("导入失败：" + e.getMessage());
        }
    }
}
