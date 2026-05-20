package com.example.lebei;

import java.util.List;

public final class LearnProgressPolicy {
    public static final int NO_NEXT_INDEX = -1;

    private LearnProgressPolicy() {}

    public static int firstUnlearnedIndex(List<Integer> learnedFlags, int wordCount) {
        if (learnedFlags == null || learnedFlags.isEmpty() || wordCount <= 0) {
            return NO_NEXT_INDEX;
        }
        int limit = Math.min(learnedFlags.size(), wordCount);
        for (int i = 0; i < limit; i++) {
            Integer learned = learnedFlags.get(i);
            if (learned == null || learned == 0) {
                return i;
            }
        }
        return NO_NEXT_INDEX;
    }
}
