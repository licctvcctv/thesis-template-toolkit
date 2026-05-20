package com.example.lebei;

import androidx.room.ColumnInfo;
import androidx.room.Entity;
import androidx.room.ForeignKey;
import androidx.room.Index;
import androidx.room.PrimaryKey;

@Entity(
        tableName = "daily_plan_word",
        foreignKeys = {
            @ForeignKey(
                    entity = DailyPlan.class,
                    parentColumns = "id",
                    childColumns = "daily_plan_id",
                    onDelete = ForeignKey.CASCADE),
            @ForeignKey(
                    entity = Word.class,
                    parentColumns = "id",
                    childColumns = "word_id",
                    onDelete = ForeignKey.CASCADE)
        },
        indices = {
            @Index("daily_plan_id"),
            @Index("word_id"),
            @Index(value = {"daily_plan_id", "word_id"}, unique = true)
        })
public class DailyPlanWord {
    @PrimaryKey(autoGenerate = true)
    public long id;

    @ColumnInfo(name = "daily_plan_id")
    public long dailyPlanId;

    @ColumnInfo(name = "word_id")
    public int wordId;

    @ColumnInfo(name = "sort_order")
    public int sortOrder;

    @ColumnInfo(name = "ai_example_text")
    public String aiExampleText;

    /** 1 表示用户当日已对该词点击简单/困难，计入「今日已学」 */
    @ColumnInfo(name = "learned")
    public int learned;

    public DailyPlanWord(long dailyPlanId, int wordId, int sortOrder) {
        this.dailyPlanId = dailyPlanId;
        this.wordId = wordId;
        this.sortOrder = sortOrder;
        this.aiExampleText = null;
        this.learned = 0;
    }
}
