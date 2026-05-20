package com.example.lebei;

import androidx.room.Entity;
import androidx.room.Ignore;
import androidx.room.PrimaryKey;

@Entity(tableName = "word_table")
public class Word {
    @PrimaryKey(autoGenerate = true)
    public int id;

    public String word;
    public String phonetic;
    public String translation;
    public String bookId;       // 所属词库ID
    /** 词库难度标签：0 简单，1 困难。来自 CSV 第五列。 */
    public int difficultyTag;

    // 学习进度
    public int familiarity;      // 0-6 权重：0 未学，5 已学，6 掌握
    public long nextReviewTime;  // 下次复习时间戳
    public int reviewCount;      // 复习次数

    public Word() {}

    @Ignore
    public Word(String word, String phonetic, String translation, String bookId) {
        this(word, phonetic, translation, bookId, 0);
    }

    @Ignore
    public Word(String word, String phonetic, String translation, String bookId, int difficultyTag) {
        this.word = word;
        this.phonetic = phonetic;
        this.translation = translation;
        this.bookId = bookId;
        this.difficultyTag = difficultyTag;
        this.familiarity = 0;
        this.nextReviewTime = System.currentTimeMillis();
        this.reviewCount = 0;
    }
}
