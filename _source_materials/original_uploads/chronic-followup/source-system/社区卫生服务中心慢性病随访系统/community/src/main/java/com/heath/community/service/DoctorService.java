package com.heath.community.service;

import com.heath.community.common.PageResult;
import com.heath.community.dto.DoctorDTO;
import com.heath.community.entity.Doctor;
import com.heath.community.entity.User;
import com.heath.community.mapper.DoctorMapper;
import com.heath.community.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class DoctorService {
    private final DoctorMapper doctorMapper;
    private final UserMapper userMapper;

    public PageResult<DoctorDTO> findPage(String name, String employeeId, String department, Long current, Long size) {
        Long offset = (current - 1) * size;
        List<DoctorDTO> records = doctorMapper.findPage(name, employeeId, department, offset, size);
        Long total = doctorMapper.count(name, employeeId, department);
        return PageResult.of(records, total, current, size);
    }

    public DoctorDTO findById(Long id) {
        return doctorMapper.findById(id);
    }

    public DoctorDTO findByUserId(Long userId) {
        Doctor doctor = doctorMapper.findByUserId(userId);
        if (doctor == null) {
            return null;
        }
        return doctorMapper.findById(doctor.getId());
    }

    @Transactional
    public void add(DoctorDTO dto) {
        User existingUser = userMapper.findByUsername(dto.getUsername());
        if (existingUser != null) {
            throw new RuntimeException("用户名已存在");
        }

        User user = new User();
        user.setUsername(dto.getUsername());
        user.setPassword("123456");
        user.setName(dto.getName());
        user.setRole("doctor");
        user.setStatus(1);
        userMapper.insert(user);

        Doctor doctor = new Doctor();
        doctor.setUserId(user.getId());
        doctor.setEmployeeId(dto.getEmployeeId());
        doctor.setPhone(dto.getPhone());
        doctor.setEmail(dto.getEmail());
        doctor.setDepartment(dto.getDepartment());
        doctor.setTitle(dto.getTitle());
        doctor.setSpecialty(dto.getSpecialty());
        doctorMapper.insert(doctor);
    }

    @Transactional
    public void update(DoctorDTO dto) {
        DoctorDTO existing = doctorMapper.findById(dto.getId());
        if (existing == null) {
            throw new RuntimeException("医生不存在");
        }

        User user = userMapper.findById(existing.getUserId());
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }

        if (dto.getUsername() != null && !dto.getUsername().equals(user.getUsername())) {
            User existingUser = userMapper.findByUsername(dto.getUsername());
            if (existingUser != null && !existingUser.getId().equals(user.getId())) {
                throw new RuntimeException("用户名已存在");
            }
            user.setUsername(dto.getUsername());
        }

        if (dto.getName() != null) {
            user.setName(dto.getName());
        }
        userMapper.update(user);

        Doctor doctor = doctorMapper.findByUserId(user.getId());
        if (doctor == null) {
            throw new RuntimeException("医生信息不存在");
        }

        if (dto.getEmployeeId() != null) {
            doctor.setEmployeeId(dto.getEmployeeId());
        }
        if (dto.getPhone() != null) {
            doctor.setPhone(dto.getPhone());
        }
        if (dto.getEmail() != null) {
            doctor.setEmail(dto.getEmail());
        }
        if (dto.getDepartment() != null) {
            doctor.setDepartment(dto.getDepartment());
        }
        if (dto.getTitle() != null) {
            doctor.setTitle(dto.getTitle());
        }
        if (dto.getSpecialty() != null) {
            doctor.setSpecialty(dto.getSpecialty());
        }
        doctorMapper.update(doctor);
    }

    @Transactional
    public void delete(Long id) {
        DoctorDTO doctor = doctorMapper.findById(id);
        if (doctor == null) {
            throw new RuntimeException("医生不存在");
        }
        doctorMapper.delete(id);
        userMapper.delete(doctor.getUserId());
    }

    public void updateStatus(Long id, Integer status) {
        DoctorDTO doctor = doctorMapper.findById(id);
        if (doctor == null) {
            throw new RuntimeException("医生不存在");
        }
        userMapper.updateStatus(doctor.getUserId(), status);
    }
}
