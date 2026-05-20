package com.example.lebei;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;

/** 从词库中按「日期 + 词库」稳定随机选词，并排除与昨日计划重复的词。 */
public final class DailyWordPicker {

    private DailyWordPicker() {}

    public static List<Integer> pickWordIds(
            WordDao wordDao,
            DailyPlanDao dailyPlanDao,
            String todayDateKey,
            String bookId,
            int targetCount,
            String yesterdayDateKey) {
        List<Integer> all = wordDao.getWordIdsInBook(bookId);
        if (all == null || all.isEmpty()) {
            return new ArrayList<>();
        }

        Set<Integer> excludeYesterday = new HashSet<>();
        if (yesterdayDateKey != null && !yesterdayDateKey.isEmpty()) {
            List<Integer> y = dailyPlanDao.getWordIdsForDateAndBook(yesterdayDateKey, bookId);
            if (y != null) {
                excludeYesterday.addAll(y);
            }
        }

        List<Integer> pool = new ArrayList<>();
        for (Integer id : all) {
            if (!excludeYesterday.contains(id)) {
                pool.add(id);
            }
        }
        if (pool.isEmpty()) {
            pool = new ArrayList<>(all);
        }

        Random rnd = randomForDay(todayDateKey, bookId);
        Collections.shuffle(pool, rnd);

        int n = Math.min(targetCount, pool.size());
        return new ArrayList<>(pool.subList(0, n));
    }

    /**
     * 从词库随机抽取若干「新词」id，排除昨日计划中的词及 {@code excludeIds}（例如已放入今日复习的词）。
     */
    public static List<Integer> pickNewWordIds(
            WordDao wordDao,
            DailyPlanDao dailyPlanDao,
            String todayDateKey,
            String bookId,
            int newWordCount,
            String yesterdayDateKey,
            Set<Integer> excludeIds) {
        if (newWordCount <= 0) {
            return new ArrayList<>();
        }
        List<Integer> all = wordDao.getWordIdsInBook(bookId);
        if (all == null || all.isEmpty()) {
            return new ArrayList<>();
        }

        Set<Integer> exclude = new HashSet<>();
        if (excludeIds != null) {
            exclude.addAll(excludeIds);
        }
        if (yesterdayDateKey != null && !yesterdayDateKey.isEmpty()) {
            List<Integer> y = dailyPlanDao.getWordIdsForDateAndBook(yesterdayDateKey, bookId);
            if (y != null) {
                exclude.addAll(y);
            }
        }

        List<Integer> pool = new ArrayList<>();
        for (Integer id : all) {
            if (!exclude.contains(id)) {
                pool.add(id);
            }
        }
        if (pool.isEmpty()) {
            for (Integer id : all) {
                if (excludeIds == null || !excludeIds.contains(id)) {
                    pool.add(id);
                }
            }
        }
        if (pool.isEmpty()) {
            pool = new ArrayList<>(all);
        }

        Random rnd = randomForDay(todayDateKey, bookId);
        Collections.shuffle(pool, rnd);
        int n = Math.min(newWordCount, pool.size());
        return new ArrayList<>(pool.subList(0, n));
    }

    private static Random randomForDay(String dateKey, String bookId) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest((dateKey + "|" + bookId).getBytes(StandardCharsets.UTF_8));
            long seed = 0;
            for (int i = 0; i < 8 && i < digest.length; i++) {
                seed = (seed << 8) | (digest[i] & 0xffL);
            }
            return new Random(seed);
        } catch (NoSuchAlgorithmException e) {
            return new Random((dateKey + "|" + bookId).hashCode());
        }
    }
}
