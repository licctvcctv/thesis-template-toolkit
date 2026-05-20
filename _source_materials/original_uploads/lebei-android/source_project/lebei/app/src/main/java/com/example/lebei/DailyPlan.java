package com.example.lebei;

import androidx.annotation.NonNull;
import androidx.room.ColumnInfo;
import androidx.room.Entity;
import androidx.room.Index;
import androidx.room.PrimaryKey;

@Entity(
        tableName = "daily_plan",
        indices = {@Index(value = {"date_key", "book_id"}, unique = true)})
public class DailyPlan {
    @PrimaryKey(autoGenerate = true)
    public long id;

    @NonNull
    @ColumnInfo(name = "date_key")
    public String dateKey;

    @NonNull
    @ColumnInfo(name = "book_id")
    public String bookId;

    /** 当日 AI 短文全文，未生成时为 null */
    @ColumnInfo(name = "essay_text")
    public String essayText;

    /** 计划抽取的单词数量目标 */
    @ColumnInfo(name = "target_count")
    public int targetCount;

    public DailyPlan(String dateKey, String bookId, int targetCount) {
        this.dateKey = dateKey;
        this.bookId = bookId;
        this.essayText = null;
        this.targetCount = targetCount;
    }
}
