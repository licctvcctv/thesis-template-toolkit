package com.heath.community.mapper;

import com.heath.community.entity.Department;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface DepartmentMapper {
    List<Department> findPage(@Param("name") String name, @Param("offset") Long offset, @Param("limit") Long limit);
    Long count(@Param("name") String name);
    List<Department> findAllEnabled();
    Department findById(@Param("id") Long id);
    Department findByName(@Param("name") String name);
    int insert(Department department);
    int update(Department department);
    int delete(@Param("id") Long id);
}
