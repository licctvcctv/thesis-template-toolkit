package com.example.lebei;

import java.util.Locale;

public final class WordReviewPolicy {
    public static final int MIN_WEIGHT = 0;
    public static final int HARD_LEARNED_WEIGHT = 4;
    public static final int LEARNED_WEIGHT = 5;
    public static final int MASTERED_WEIGHT = 6;

    public static final long WRONG_REVIEW_DELAY_MS = 10 * 60 * 1000L;
    public static final long SAME_DAY_NEW_WORD_REVIEW_DELAY_MS = 0L;
    public static final long LEARNED_REVIEW_DELAY_MS = 24 * 60 * 60 * 1000L;
    public static final long MASTERED_DECAY_DELAY_MS = 3 * 24 * 60 * 60 * 1000L;

    private WordReviewPolicy() {}

    public static int weightAfterNewWord(boolean easy) {
        return easy ? LEARNED_WEIGHT : HARD_LEARNED_WEIGHT;
    }

    public static int weightAfterSpellingResult(int currentWeight, boolean correct) {
        int next = correct ? currentWeight + 1 : currentWeight - 1;
        return clampWeight(next);
    }

    public static boolean isMastered(int weight) {
        return weight > LEARNED_WEIGHT;
    }

    public static boolean isReviewCandidate(int weight) {
        return weight > MIN_WEIGHT && weight <= LEARNED_WEIGHT;
    }

    public static long nextReviewTime(long now, int newWeight, boolean correct) {
        if (!correct && newWeight <= HARD_LEARNED_WEIGHT) {
            return now + WRONG_REVIEW_DELAY_MS;
        }
        if (newWeight >= MASTERED_WEIGHT) {
            return now + MASTERED_DECAY_DELAY_MS;
        }
        return now + LEARNED_REVIEW_DELAY_MS;
    }

    public static long firstSameDayReviewTime(long now) {
        return now + SAME_DAY_NEW_WORD_REVIEW_DELAY_MS;
    }

    public static boolean spellingsMatch(String expected, String actual) {
        return normalizeSpelling(expected).equals(normalizeSpelling(actual));
    }

    public static String normalizeSpelling(String value) {
        if (value == null) {
            return "";
        }
        return value.trim()
                .toLowerCase(Locale.US)
                .replaceAll("[^a-z'\\-\\s]", " ")
                .replaceAll("\\s+", " ")
                .trim();
    }

    private static int clampWeight(int weight) {
        if (weight < MIN_WEIGHT) {
            return MIN_WEIGHT;
        }
        if (weight > MASTERED_WEIGHT) {
            return MASTERED_WEIGHT;
        }
        return weight;
    }
}
