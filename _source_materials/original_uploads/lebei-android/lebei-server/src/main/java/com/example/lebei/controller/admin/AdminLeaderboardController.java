package com.example.lebei.controller.admin;

import com.example.lebei.dto.LeaderboardEntryDto;
import com.example.lebei.service.UserService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin/leaderboard")
public class AdminLeaderboardController {

    private final UserService userService;

    public AdminLeaderboardController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public List<LeaderboardEntryDto> list(@RequestParam(defaultValue = "100") int limit) {
        return userService.leaderboardAppUsers(limit);
    }
}
