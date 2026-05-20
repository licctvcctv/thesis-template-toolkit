package com.example.lebei.controller.app;

import com.example.lebei.dto.AuthResponse;
import com.example.lebei.dto.LoginRequest;
import com.example.lebei.dto.RegisterRequest;
import com.example.lebei.service.UserService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/app/auth")
public class AppAuthController {

    private final UserService userService;

    public AppAuthController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/register")
    public AuthResponse register(@Valid @RequestBody RegisterRequest request) {
        return userService.registerAppUser(request);
    }

    @PostMapping("/login")
    public AuthResponse login(@Valid @RequestBody LoginRequest request) {
        return userService.loginAppUser(request);
    }
}
