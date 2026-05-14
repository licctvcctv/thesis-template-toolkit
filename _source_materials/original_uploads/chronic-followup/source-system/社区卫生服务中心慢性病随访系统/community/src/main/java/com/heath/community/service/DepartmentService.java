package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.entity.Department;
import com.heath.community.mapper.DepartmentMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class DepartmentService {
    private final DepartmentMapper departmentMapper;

    public PageResult<Department> findPage(String name, Long current, Long size) {
        Long offset = (current - 1) * size;
        List<Department> records = departmentMapper.findPage(name, offset, size);
        Long total = departmentMapper.count(name);
        return PageResult.of(records, total, current, size);
    }

    public List<Department> findAllEnabled() {
        return departmentMapper.findAllEnabled();
    }

    public Department findById(Long id) {
        return departmentMapper.findById(id);
    }

    public void add(Department department) {
        Department existing = departmentMapper.findByName(department.getName());
        if (existing != null) {
            throw new RuntimeException("科室名称已存在");
        }
        if (department.getStatus() == null) {
            department.setStatus(1);
        }
        departmentMapper.insert(department);
    }

    public void update(Department department) {
        Department existing = departmentMapper.findById(department.getId());
        if (existing == null) {
            throw new RuntimeException("科室不存在");
        }
        
        if (department.getName() != null && !department.getName().equals(existing.getName())) {
            Department duplicate = departmentMapper.findByName(department.getName());
            if (duplicate != null && !duplicate.getId().equals(department.getId())) {
                throw new RuntimeException("科室名称已存在");
            }
        }
        
        departmentMapper.update(department);
    }

    public void delete(Long id) {
        Department department = departmentMapper.findById(id);
        if (department == null) {
            throw new RuntimeException("科室不存在");
        }
        departmentMapper.delete(id);
    }
}
