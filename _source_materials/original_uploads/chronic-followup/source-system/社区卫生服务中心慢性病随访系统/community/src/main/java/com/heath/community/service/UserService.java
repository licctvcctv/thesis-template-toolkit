package com.heath.community.service;

import com.heath.community.dto.ChangePasswordDTO;
import com.heath.community.dto.LoginRequest;
import com.heath.community.dto.LoginResponse;
import com.heath.community.dto.UpdateUserInfoDTO;
import com.heath.community.entity.User;
import com.heath.community.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserMapper userMapper;

    public LoginResponse login(LoginRequest request) {
        User user = userMapper.findByUsername(request.getUsername());
        if (user == null) {
            throw new RuntimeException("用户名不存在");
        }
        if (!user.getPassword().equals(request.getPassword())) {
            throw new RuntimeException("密码错误");
        }
        if (user.getStatus() == 0) {
            throw new RuntimeException("账号已被禁用");
        }

        LoginResponse response = new LoginResponse();
        response.setId(user.getId());
        response.setUsername(user.getUsername());
        response.setName(user.getName());
        response.setRole(user.getRole());
        response.setToken(user.getId().toString());
        return response;
    }

    public User findById(Long id) {
        return userMapper.findById(id);
    }

    @Transactional
    public void updateUserInfo(Long id, UpdateUserInfoDTO dto) {
        User user = userMapper.findById(id);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        user.setName(dto.getName());
        userMapper.update(user);
    }

    @Transactional
    public void changePassword(Long id, ChangePasswordDTO dto) {
        User user = userMapper.findById(id);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        if (!user.getPassword().equals(dto.getOldPassword())) {
            throw new RuntimeException("原密码错误");
        }
        userMapper.updatePassword(id, dto.getNewPassword());
    }
}
