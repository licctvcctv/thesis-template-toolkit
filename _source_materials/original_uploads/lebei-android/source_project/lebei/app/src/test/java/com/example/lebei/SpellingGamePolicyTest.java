package com.example.lebei;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class SpellingGamePolicyTest {

    @Test
    public void correctAnswerAddsOnePointAndAnsweredCount() {
        assertEquals(4, SpellingGamePolicy.scoreAfterAnswer(3, true));
        assertEquals(6, SpellingGamePolicy.answeredAfterSubmit(5));
    }

    @Test
    public void wrongAnswerDoesNotAddPointButStillCountsAsAnswered() {
        assertEquals(3, SpellingGamePolicy.scoreAfterAnswer(3, false));
        assertEquals(6, SpellingGamePolicy.answeredAfterSubmit(5));
    }

    @Test
    public void timeIsUpAtGameDuration() {
        long start = 10_000L;

        assertFalse(SpellingGamePolicy.isTimeUp(start, start + SpellingGamePolicy.GAME_DURATION_MS - 1));
        assertTrue(SpellingGamePolicy.isTimeUp(start, start + SpellingGamePolicy.GAME_DURATION_MS));
    }
}
