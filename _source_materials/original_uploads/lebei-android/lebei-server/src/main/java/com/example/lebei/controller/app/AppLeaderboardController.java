package com.example.lebei.controller.app;

import com.example.lebei.dto.LeaderboardEntryDto;
import com.example.lebei.service.UserService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/app/leaderboard")
public class AppLeaderboardController {

    private final UserService userService;

    public AppLeaderboardController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public List<LeaderboardEntryDto> list(@RequestParam(defaultValue = "50") int limit) {
        return userService.leaderboardAppUsers(limit);
    }
}
