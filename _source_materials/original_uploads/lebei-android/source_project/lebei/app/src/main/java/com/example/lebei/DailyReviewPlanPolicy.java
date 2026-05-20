package com.example.lebei;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public final class DailyReviewPlanPolicy {

    private DailyReviewPlanPolicy() {}

    public static List<Integer> dueIdsToReopen(
            List<Integer> existingIds, List<Integer> learnedFlags, List<Integer> dueIds) {
        List<Integer> out = new ArrayList<>();
        if (existingIds == null || learnedFlags == null || dueIds == null) {
            return out;
        }
        Set<Integer> uniqueDue = new LinkedHashSet<>(dueIds);
        int limit = Math.min(existingIds.size(), learnedFlags.size());
        for (int i = 0; i < limit; i++) {
            Integer wordId = existingIds.get(i);
            Integer learned = learnedFlags.get(i);
            if (wordId != null && uniqueDue.contains(wordId) && learned != null && learned != 0) {
                out.add(wordId);
            }
        }
        return out;
    }

    public static List<Integer> dueIdsToAppend(List<Integer> existingIds, List<Integer> dueIds) {
        List<Integer> out = new ArrayList<>();
        if (dueIds == null || dueIds.isEmpty()) {
            return out;
        }
        Set<Integer> existing = new LinkedHashSet<>();
        if (existingIds != null) {
            existing.addAll(existingIds);
        }
        for (Integer wordId : new LinkedHashSet<>(dueIds)) {
            if (wordId != null && !existing.contains(wordId)) {
                out.add(wordId);
            }
        }
        return out;
    }

    public static List<Integer> newThenReviewIds(List<Integer> reviewIds, List<Integer> newIds) {
        List<Integer> reviews = uniqueNonNull(reviewIds);
        List<Integer> news = uniqueNonNull(newIds);
        news.removeAll(new LinkedHashSet<>(reviews));
        List<Integer> out = new ArrayList<>(reviews.size() + news.size());
        out.addAll(news);
        out.addAll(reviews);
        return out;
    }

    public static List<Integer> reorderExistingPlanIdsForDueReviews(
            List<Integer> existingIds, List<Integer> learnedFlags, List<Integer> dueIds) {
        List<Integer> completedIds = new ArrayList<>();
        List<Integer> pendingNewIds = new ArrayList<>();
        Set<Integer> uniqueDue = new LinkedHashSet<>(dueIds != null ? dueIds : new ArrayList<>());
        Set<Integer> seenExisting = new LinkedHashSet<>();
        if (existingIds != null) {
            int limit = existingIds.size();
            for (int i = 0; i < limit; i++) {
                Integer wordId = existingIds.get(i);
                if (wordId == null || !seenExisting.add(wordId) || uniqueDue.contains(wordId)) {
                    continue;
                }
                Integer learned =
                        learnedFlags != null && i < learnedFlags.size() ? learnedFlags.get(i) : 0;
                if (learned != null && learned != 0) {
                    completedIds.add(wordId);
                } else {
                    pendingNewIds.add(wordId);
                }
            }
        }

        List<Integer> out = new ArrayList<>(completedIds);
        out.addAll(newThenReviewIds(new ArrayList<>(uniqueDue), pendingNewIds));
        return out;
    }

    private static List<Integer> uniqueNonNull(List<Integer> ids) {
        List<Integer> out = new ArrayList<>();
        if (ids == null || ids.isEmpty()) {
            return out;
        }
        for (Integer id : new LinkedHashSet<>(ids)) {
            if (id != null) {
                out.add(id);
            }
        }
        return out;
    }
}
