package com.example.lebei;

import static org.junit.Assert.assertEquals;

import java.util.Arrays;
import java.util.Collections;
import org.junit.Test;

public class LearnProgressPolicyTest {

    @Test
    public void firstUnlearnedIndexFindsNextPendingWord() {
        assertEquals(1, LearnProgressPolicy.firstUnlearnedIndex(Arrays.asList(1, 0, 0), 3));
    }

    @Test
    public void firstUnlearnedIndexReturnsNoNextWhenPlanIsComplete() {
        assertEquals(
                LearnProgressPolicy.NO_NEXT_INDEX,
                LearnProgressPolicy.firstUnlearnedIndex(Arrays.asList(1, 1), 2));
    }

    @Test
    public void firstUnlearnedIndexReturnsNoNextForEmptyPlan() {
        assertEquals(
                LearnProgressPolicy.NO_NEXT_INDEX,
                LearnProgressPolicy.firstUnlearnedIndex(Collections.emptyList(), 0));
    }
}
