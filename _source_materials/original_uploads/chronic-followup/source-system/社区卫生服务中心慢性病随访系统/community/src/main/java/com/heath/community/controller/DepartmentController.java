package com.heath.community.controller;

import com.heath.community.common.PageResult;
import com.heath.community.common.Result;
import com.heath.community.entity.Department;
import com.heath.community.service.DepartmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/department")
@RequiredArgsConstructor
public class DepartmentController {
    private final DepartmentService departmentService;

    @GetMapping("/list")
    public Result<PageResult<Department>> list(@RequestParam(required = false) String name,
                                               @RequestParam(defaultValue = "1") Long current,
                                               @RequestParam(defaultValue = "10") Long size) {
        PageResult<Department> pageResult = departmentService.findPage(name, current, size);
        return Result.success(pageResult);
    }

    @GetMapping("/enabled")
    public Result<List<Department>> listEnabled() {
        List<Department> list = departmentService.findAllEnabled();
        return Result.success(list);
    }

    @GetMapping("/{id}")
    public Result<Department> getById(@PathVariable Long id) {
        Department department = departmentService.findById(id);
        return Result.success(department);
    }

    @PostMapping("/add")
    public Result<Void> add(@RequestBody Department department) {
        try {
            departmentService.add(department);
            return Result.success("添加成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @PutMapping("/update")
    public Result<Void> update(@RequestBody Department department) {
        try {
            departmentService.update(department);
            return Result.success("更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        try {
            departmentService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }
}
