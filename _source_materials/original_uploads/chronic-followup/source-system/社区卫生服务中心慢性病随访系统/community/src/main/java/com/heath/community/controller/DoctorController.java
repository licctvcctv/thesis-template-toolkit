package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.dto.DoctorDTO;
import com.heath.community.service.DoctorService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/doctor")
@RequiredArgsConstructor
public class DoctorController {
    private final DoctorService doctorService;

    @GetMapping("/list")
    public Result<PageResult<DoctorDTO>> list(@RequestParam(required = false) String name,
                                              @RequestParam(required = false) String employeeId,
                                              @RequestParam(required = false) String department,
                                              @RequestParam(defaultValue = "1") Long current,
                                              @RequestParam(defaultValue = "10") Long size) {
        PageResult<DoctorDTO> pageResult = doctorService.findPage(name, employeeId, department, current, size);
        return Result.success(pageResult);
    }

    @GetMapping("/{id}")
    public Result<DoctorDTO> getById(@PathVariable Long id) {
        DoctorDTO doctor = doctorService.findById(id);
        return Result.success(doctor);
    }

    @GetMapping("/by-user/{userId}")
    public Result<DoctorDTO> getByUserId(@PathVariable Long userId) {
        DoctorDTO doctor = doctorService.findByUserId(userId);
        return Result.success(doctor);
    }

    @PostMapping("/add")
    public Result<Void> add(@RequestBody DoctorDTO dto) {
        try {
            doctorService.add(dto);
            return Result.success("添加成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @PutMapping("/update")
    public Result<Void> update(@RequestBody DoctorDTO dto) {
        try {
            doctorService.update(dto);
            return Result.success("更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        try {
            doctorService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @PutMapping("/status/{id}")
    public Result<Void> updateStatus(@PathVariable Long id, @RequestParam Integer status) {
        try {
            doctorService.updateStatus(id, status);
            return Result.success("状态更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
