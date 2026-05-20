package com.example.lebei;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class WordReviewPolicyTest {

    @Test
    public void newWordEasyStartsAtLearnedWeight() {
        assertEquals(5, WordReviewPolicy.weightAfterNewWord(true));
    }

    @Test
    public void newWordHardIsLearnedButDueSoon() {
        assertEquals(4, WordReviewPolicy.weightAfterNewWord(false));
    }

    @Test
    public void correctSpellingRaisesWeightAndCapsAtMastered() {
        assertEquals(6, WordReviewPolicy.weightAfterSpellingResult(5, true));
        assertEquals(6, WordReviewPolicy.weightAfterSpellingResult(6, true));
        assertTrue(WordReviewPolicy.isMastered(6));
        assertFalse(WordReviewPolicy.isMastered(5));
    }

    @Test
    public void wrongSpellingLowersWeightAndNeverGoesBelowZero() {
        assertEquals(4, WordReviewPolicy.weightAfterSpellingResult(5, false));
        assertEquals(0, WordReviewPolicy.weightAfterSpellingResult(0, false));
    }

    @Test
    public void spellingComparisonIgnoresCaseAndExtraSpacing() {
        assertTrue(WordReviewPolicy.spellingsMatch("  New   York  ", "new york"));
        assertTrue(WordReviewPolicy.spellingsMatch("Mother-in-law", " mother-in-law "));
        assertFalse(WordReviewPolicy.spellingsMatch("affect", "effect"));
    }

    @Test
    public void nextReviewTimeUsesShortDelayForWrongAndLongerDelayForMastered() {
        long now = 1_000_000L;

        assertEquals(now + WordReviewPolicy.WRONG_REVIEW_DELAY_MS, WordReviewPolicy.nextReviewTime(now, 4, false));
        assertEquals(now + WordReviewPolicy.LEARNED_REVIEW_DELAY_MS, WordReviewPolicy.nextReviewTime(now, 5, true));
        assertEquals(now + WordReviewPolicy.MASTERED_DECAY_DELAY_MS, WordReviewPolicy.nextReviewTime(now, 6, true));
    }

    @Test
    public void newlyLearnedWordsCanBeReviewedSameDay() {
        long now = 1_000_000L;

        assertEquals(now, WordReviewPolicy.firstSameDayReviewTime(now));
    }
}
