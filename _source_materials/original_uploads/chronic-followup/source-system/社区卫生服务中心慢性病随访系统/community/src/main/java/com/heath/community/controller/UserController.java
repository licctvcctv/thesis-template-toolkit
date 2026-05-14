package com.heath.community.controller;

import com.heath.community.common.Result;
import com.heath.community.dto.ChangePasswordDTO;
import com.heath.community.dto.UpdateUserInfoDTO;
import com.heath.community.entity.User;
import com.heath.community.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping("/current")
    public Result<User> getCurrent(@RequestParam Long userId) {
        User user = userService.findById(userId);
        // 不返回密码
        user.setPassword(null);
        return Result.success(user);
    }

    @PutMapping("/info")
    public Result<Void> updateUserInfo(@RequestParam Long userId, @RequestBody UpdateUserInfoDTO dto) {
        userService.updateUserInfo(userId, dto);
        return Result.success();
    }

    @PutMapping("/password")
    public Result<Void> changePassword(@RequestParam Long userId, @RequestBody ChangePasswordDTO dto) {
        userService.changePassword(userId, dto);
        return Result.success();
    }
}
