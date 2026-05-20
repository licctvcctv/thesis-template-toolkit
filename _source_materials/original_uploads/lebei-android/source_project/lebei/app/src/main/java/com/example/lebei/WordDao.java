package com.example.lebei;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.Query;
import androidx.room.Update;
import java.util.ArrayList;
import java.util.List;

@Dao
public interface WordDao {
    @Insert
    void insert(Word word);

    @Insert
    void insertAll(List<Word> words);

    @Update
    void update(Word word);

    @Query("SELECT * FROM word_table WHERE bookId = :bookId")
    List<Word> getWordsByBook(String bookId);

    @Query("SELECT id FROM word_table WHERE bookId = :bookId")
    List<Integer> getWordIdsInBook(String bookId);

    @Query("SELECT * FROM word_table WHERE id IN (:ids)")
    List<Word> getWordsByIds(List<Integer> ids);

    /**
     * SQLite 单条语句绑定变量数有上限（常见 999），当日计划词很多时需分批 IN 查询，否则会抛异常。
     */
    default List<Word> getWordsByIdsChunked(List<Integer> ids) {
        if (ids == null || ids.isEmpty()) {
            return new ArrayList<>();
        }
        final int chunk = 500;
        List<Word> out = new ArrayList<>(Math.min(ids.size(), 64));
        for (int i = 0; i < ids.size(); i += chunk) {
            int end = Math.min(i + chunk, ids.size());
            List<Integer> sub = new ArrayList<>(ids.subList(i, end));
            List<Word> part = getWordsByIds(sub);
            if (part != null) {
                out.addAll(part);
            }
        }
        return out;
    }

    @Query(
            "SELECT * FROM word_table "
                    + "WHERE familiarity > 0 AND familiarity <= 5 AND nextReviewTime <= :currentTime "
                    + "ORDER BY familiarity ASC, nextReviewTime ASC, difficultyTag DESC "
                    + "LIMIT :limit")
    List<Word> getWordsForReview(long currentTime, int limit);

    @Query(
            "SELECT * FROM word_table "
                    + "WHERE familiarity > 0 AND familiarity <= 5 AND nextReviewTime <= :currentTime "
                    + "ORDER BY familiarity ASC, nextReviewTime ASC, difficultyTag DESC "
                    + "LIMIT :limit")
    List<Word> getGameDueWords(long currentTime, int limit);

    @Query(
            "SELECT * FROM word_table "
                    + "WHERE familiarity > 0 "
                    + "ORDER BY familiarity ASC, nextReviewTime ASC, difficultyTag DESC "
                    + "LIMIT :limit")
    List<Word> getGameLearnedWords(int limit);

    @Query("SELECT * FROM word_table WHERE bookId = :bookId AND familiarity = 0 ORDER BY id ASC LIMIT :limit")
    List<Word> getNewWords(String bookId, int limit);

    // 统计相关
    @Query("SELECT COUNT(*) FROM word_table")
    int getTotalWordsCount();

    @Query("SELECT COUNT(*) FROM word_table WHERE bookId = :bookId")
    int countWordsInBook(String bookId);

    @Query("SELECT COUNT(*) FROM word_table WHERE bookId = :bookId AND difficultyTag != 0")
    int countDifficultyTaggedWordsInBook(String bookId);

    @Query("UPDATE word_table SET difficultyTag = :difficultyTag WHERE bookId = :bookId AND word = :word")
    void updateDifficultyTag(String bookId, String word, int difficultyTag);

    @Query("SELECT COUNT(*) FROM word_table WHERE familiarity > 0")
    int getLearnedWordsCount();
    // 已掌握单词数（权重大于 5 视为掌握）
    @Query("SELECT COUNT(*) FROM word_table WHERE familiarity > 5")
    int getMasteredWordsCount();

    @Query("UPDATE word_table SET familiarity = 5, nextReviewTime = :now WHERE familiarity > 5 AND nextReviewTime <= :now")
    void decayMasteredWords(long now);

    // 总复习次数（无数据时 SUM 为 NULL，须 COALESCE 避免 Room 映射 int 崩溃）
    @Query("SELECT COALESCE(SUM(reviewCount), 0) FROM word_table")
    int getTotalReviewsCount();

    // 最早学习时间（无匹配行时 MIN 为 NULL，须 COALESCE）
    @Query("SELECT COALESCE(MIN(nextReviewTime), 0) FROM word_table WHERE reviewCount > 0")
    long getFirstLearnTime();

    @Query("UPDATE word_table SET familiarity = 0, nextReviewTime = :now, reviewCount = 0")
    void resetAllLearningProgress(long now);
}
