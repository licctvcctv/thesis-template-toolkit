package com.example.lebei.controller.admin;

import com.example.lebei.dto.AuthResponse;
import com.example.lebei.dto.LoginRequest;
import com.example.lebei.service.UserService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin/auth")
public class AdminAuthController {

    private final UserService userService;

    public AdminAuthController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/login")
    public AuthResponse login(@Valid @RequestBody LoginRequest request) {
        return userService.loginAdmin(request);
    }
}
