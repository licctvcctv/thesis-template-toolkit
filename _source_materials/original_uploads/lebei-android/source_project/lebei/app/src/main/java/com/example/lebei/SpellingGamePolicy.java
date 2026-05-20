package com.example.lebei;

public final class SpellingGamePolicy {
    public static final long GAME_DURATION_MS = 60_000L;

    private SpellingGamePolicy() {}

    public static int scoreAfterAnswer(int currentScore, boolean correct) {
        return correct ? currentScore + 1 : currentScore;
    }

    public static int answeredAfterSubmit(int currentAnswered) {
        return currentAnswered + 1;
    }

    public static boolean isTimeUp(long startedAtMs, long nowMs) {
        return nowMs - startedAtMs >= GAME_DURATION_MS;
    }
}
