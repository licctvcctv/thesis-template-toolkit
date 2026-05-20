package com.example.lebei.dto;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class LeaderboardEntryDtoTest {

    @Test
    void includesMasteredWordsCount() {
        LeaderboardEntryDto entry = new LeaderboardEntryDto(1, "student", 20, 7, 30, 5);

        assertThat(entry.getMasteredWordsCount()).isEqualTo(7);
    }
}
