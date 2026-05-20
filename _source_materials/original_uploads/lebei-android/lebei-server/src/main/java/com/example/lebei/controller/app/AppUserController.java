package com.example.lebei.controller.app;

import com.example.lebei.dto.LearnedWordsSyncRequest;
import com.example.lebei.dto.PlanPatchRequest;
import com.example.lebei.dto.ProfileUpdateRequest;
import com.example.lebei.dto.UserProfileDto;
import com.example.lebei.service.UserService;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/app/user")
public class AppUserController {

    private final UserService userService;

    public AppUserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/me")
    public UserProfileDto me(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return userService.getProfile(userId);
    }

    @PutMapping("/profile")
    public UserProfileDto updateProfile(Authentication authentication, @Valid @RequestBody ProfileUpdateRequest body) {
        Long userId = (Long) authentication.getPrincipal();
        return userService.updateProfile(userId, body);
    }

    @PutMapping("/plan")
    public UserProfileDto updatePlan(Authentication authentication, @Valid @RequestBody PlanPatchRequest body) {
        Long userId = (Long) authentication.getPrincipal();
        return userService.updatePlan(userId, body);
    }

    @PutMapping("/stats/learned-words")
    public UserProfileDto syncLearned(Authentication authentication, @Valid @RequestBody LearnedWordsSyncRequest body) {
        Long userId = (Long) authentication.getPrincipal();
        return userService.syncLearnedWords(userId, body);
    }

    @PostMapping("/stats/study-word")
    public UserProfileDto recordStudyWord(Authentication authentication) {
        Long userId = (Long) authentication.getPrincipal();
        return userService.recordStudyWord(userId);
    }
}
