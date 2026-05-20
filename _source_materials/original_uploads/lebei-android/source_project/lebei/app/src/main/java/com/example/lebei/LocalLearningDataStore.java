package com.example.lebei;

import android.content.Context;

/**
 * 本地学习数据（每日计划、例句、短文、单词熟悉度）按设备存储，切换账号时需清空以免串号。
 *
 * <p>所有对 Room 的写操作及易与「换号清空」冲突的读操作应在同一把锁上串行执行，避免多线程 SQLITE_BUSY
 * 或结构损坏导致闪退。
 */
public final class LocalLearningDataStore {

    private static final Object DB_WRITE_LOCK = new Object();

    private LocalLearningDataStore() {}

    public static void withDbLock(Runnable r) {
        synchronized (DB_WRITE_LOCK) {
            r.run();
        }
    }

    /** 删除所有每日计划（级联删除 plan_word），并重置词库中所有单词的学习进度。 */
    public static void clearForNewUser(Context appContext) {
        withDbLock(
                () -> {
                    AppDatabase db = AppDatabase.getInstance(appContext.getApplicationContext());
                    long now = System.currentTimeMillis();
                    db.runInTransaction(
                            () -> {
                                db.dailyPlanDao().deleteAllPlans();
                                db.wordDao().resetAllLearningProgress(now);
                            });
                });
    }
}
