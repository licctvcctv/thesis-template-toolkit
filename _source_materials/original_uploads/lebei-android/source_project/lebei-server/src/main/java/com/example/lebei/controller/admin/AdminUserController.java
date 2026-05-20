package com.example.lebei.controller.admin;

import com.example.lebei.dto.UserProfileDto;
import com.example.lebei.service.UserService;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
public class AdminUserController {

    private final UserService userService;

    public AdminUserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/me")
    public UserProfileDto me(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return userService.getProfile(userId);
    }
}
