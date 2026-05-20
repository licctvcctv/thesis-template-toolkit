package com.example.lebei.service;

import com.example.lebei.dto.UserProfileDto;
import com.example.lebei.entity.UserEntity;
import com.example.lebei.entity.UserRole;

public final class UserMapper {

    private UserMapper() {}

    public static UserProfileDto toDto(UserEntity e) {
        UserProfileDto d = new UserProfileDto();
        d.setId(e.getId());
        d.setUsername(e.getUsername());
        d.setAgeGroup(e.getAgeGroup());
        d.setLevel(e.getLevel());
        d.setCurrentBookId(e.getCurrentBookId());
        d.setProfileComplete(Boolean.TRUE.equals(e.getProfileComplete()));
        d.setDailyNewWords(e.getDailyNewWords());
        d.setDailyReviewWords(e.getDailyReviewWords());
        d.setLearnedWordsCount(e.getLearnedWordsCount());
        d.setMasteredWordsCount(e.getMasteredWordsCount() != null ? e.getMasteredWordsCount() : 0);
        d.setStudyPoints(e.getStudyPoints() != null ? e.getStudyPoints() : 0);
        d.setTodayLearnedCount(e.getTodayLearnedCount() != null ? e.getTodayLearnedCount() : 0);
        d.setRole(e.getRole() != null ? e.getRole().name() : UserRole.APP_USER.name());
        return d;
    }
}
