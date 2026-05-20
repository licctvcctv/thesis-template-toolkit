package com.example.lebei;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.Query;
import androidx.room.Transaction;
import java.util.List;

@Dao
public interface DailyPlanDao {

    @Query("SELECT * FROM daily_plan WHERE date_key = :dateKey AND book_id = :bookId LIMIT 1")
    DailyPlan getPlanByDateAndBook(String dateKey, String bookId);

    @Query("SELECT * FROM daily_plan WHERE id = :planId")
    DailyPlan getPlanById(long planId);

    @Insert
    long insertPlan(DailyPlan plan);

    @Insert
    void insertPlanWords(List<DailyPlanWord> words);

    @Query(
            "SELECT dpw.word_id FROM daily_plan_word dpw "
                    + "INNER JOIN daily_plan dp ON dp.id = dpw.daily_plan_id "
                    + "WHERE dp.date_key = :dateKey AND dp.book_id = :bookId")
    List<Integer> getWordIdsForDateAndBook(String dateKey, String bookId);

    @Query("SELECT * FROM daily_plan_word WHERE daily_plan_id = :planId ORDER BY sort_order ASC")
    List<DailyPlanWord> getPlanWords(long planId);

    @Query("UPDATE daily_plan SET essay_text = :essay WHERE id = :planId")
    void updateEssay(long planId, String essay);

    @Query(
            "UPDATE daily_plan_word SET ai_example_text = :text WHERE daily_plan_id = :planId AND word_id = :wordId")
    void updateExample(long planId, int wordId, String text);

    @Query("UPDATE daily_plan_word SET learned = 1 WHERE daily_plan_id = :planId AND word_id = :wordId")
    void markLearned(long planId, int wordId);

    @Query("UPDATE daily_plan_word SET learned = 0 WHERE daily_plan_id = :planId AND word_id IN (:wordIds)")
    void markUnlearned(long planId, List<Integer> wordIds);

    @Query("UPDATE daily_plan SET target_count = :targetCount WHERE id = :planId")
    void updateTargetCount(long planId, int targetCount);

    @Query("UPDATE daily_plan_word SET sort_order = :sortOrder WHERE daily_plan_id = :planId AND word_id = :wordId")
    void updateSortOrder(long planId, int wordId, int sortOrder);

    @Query("SELECT * FROM daily_plan ORDER BY date_key DESC, book_id ASC")
    List<DailyPlan> listPlansNewestFirst();

    @Query("SELECT COUNT(*) FROM daily_plan_word WHERE daily_plan_id = :planId")
    int countWordsInPlan(long planId);

    @Query("DELETE FROM daily_plan")
    void deleteAllPlans();

    @Query("DELETE FROM daily_plan WHERE id = :planId")
    void deletePlanById(long planId);

    @Transaction
    default long insertPlanWithWords(DailyPlan plan, List<DailyPlanWord> words) {
        long planId = insertPlan(plan);
        for (int i = 0; i < words.size(); i++) {
            DailyPlanWord row = words.get(i);
            row.dailyPlanId = planId;
            row.sortOrder = i;
        }
        insertPlanWords(words);
        return planId;
    }

    @Transaction
    default void updateSortOrders(long planId, List<Integer> orderedWordIds) {
        if (orderedWordIds == null) {
            return;
        }
        for (int i = 0; i < orderedWordIds.size(); i++) {
            Integer wordId = orderedWordIds.get(i);
            if (wordId != null) {
                updateSortOrder(planId, wordId, i);
            }
        }
    }
}
