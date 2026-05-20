package com.example.lebei;

/** 与计划页词库 id 一致，供 UI 展示。 */
public final class BookLabels {

    private static final String[] IDS = {
        "JUNIOR_HIGH", "SENIOR_HIGH", "CET4", "CET6", "IELTS", "TOEFL"
    };
    private static final String[] NAMES = {
        "初中词汇", "高中词汇", "大学英语四级", "大学英语六级", "雅思词汇", "托福词汇"
    };

    private BookLabels() {}

    public static String nameForBookId(String bookId) {
        if (bookId == null) {
            return "";
        }
        for (int i = 0; i < IDS.length; i++) {
            if (IDS[i].equals(bookId)) {
                return NAMES[i];
            }
        }
        return bookId;
    }
}
