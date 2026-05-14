package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.entity.Medicine;
import com.heath.community.service.MedicineService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/medicine")
@RequiredArgsConstructor
public class MedicineController {
    private final MedicineService medicineService;

    @GetMapping("/list")
    public Result<PageResult<Medicine>> list(@RequestParam(required = false) String medicineName,
                                             @RequestParam(required = false) String medicineCode,
                                             @RequestParam(defaultValue = "1") Long current,
                                             @RequestParam(defaultValue = "10") Long size) {
        PageResult<Medicine> pageResult = medicineService.findPage(medicineName, medicineCode, current, size);
        return Result.success(pageResult);
    }

    @GetMapping("/{id}")
    public Result<Medicine> getById(@PathVariable Long id) {
        Medicine medicine = medicineService.findById(id);
        return Result.success(medicine);
    }

    @PostMapping("/add")
    public Result<Void> add(@RequestBody Medicine medicine) {
        try {
            medicineService.add(medicine);
            return Result.success("添加成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @PutMapping("/update")
    public Result<Void> update(@RequestBody Medicine medicine) {
        try {
            medicineService.update(medicine);
            return Result.success("更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        try {
            medicineService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
