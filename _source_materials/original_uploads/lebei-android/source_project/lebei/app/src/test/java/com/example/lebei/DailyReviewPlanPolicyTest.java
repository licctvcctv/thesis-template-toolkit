package com.example.lebei;

import static org.junit.Assert.assertEquals;

import java.util.Arrays;
import java.util.Collections;
import org.junit.Test;

public class DailyReviewPlanPolicyTest {

    @Test
    public void dueLearnedWordsAlreadyInPlanAreReopened() {
        assertEquals(
                Collections.singletonList(2),
                DailyReviewPlanPolicy.dueIdsToReopen(
                        Arrays.asList(1, 2, 3), Arrays.asList(0, 1, 0), Arrays.asList(2, 3)));
    }

    @Test
    public void dueWordsMissingFromExistingPlanAreAppended() {
        assertEquals(
                Arrays.asList(4, 5),
                DailyReviewPlanPolicy.dueIdsToAppend(Arrays.asList(1, 2, 3), Arrays.asList(2, 4, 5, 4)));
    }

    @Test
    public void pendingWordsAreNotReopenedAgain() {
        assertEquals(
                Collections.emptyList(),
                DailyReviewPlanPolicy.dueIdsToReopen(
                        Arrays.asList(1, 2), Arrays.asList(0, 1), Collections.singletonList(1)));
    }

    @Test
    public void newWordsComeBeforeReviewPhase() {
        assertEquals(
                Arrays.asList(101, 102, 103, 104, 105, 1, 2),
                DailyReviewPlanPolicy.newThenReviewIds(
                        Arrays.asList(1, 2), Arrays.asList(101, 102, 103, 104, 105)));
    }

    @Test
    public void reviewPhaseStillDeduplicatesIds() {
        assertEquals(
                Arrays.asList(101, 102, 1, 2, 3),
                DailyReviewPlanPolicy.newThenReviewIds(
                        Arrays.asList(1, 2, 3, 2), Arrays.asList(101, 102, 1)));
    }

    @Test
    public void existingPlanKeepsCompletedRowsThenNewWordsThenReviews() {
        assertEquals(
                Arrays.asList(10, 11, 12, 2, 4),
                DailyReviewPlanPolicy.reorderExistingPlanIdsForDueReviews(
                        Arrays.asList(10, 11, 12, 2, 4),
                        Arrays.asList(1, 0, 0, 1, 0),
                        Arrays.asList(2, 4)));
    }
}
