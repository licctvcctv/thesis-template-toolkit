package com.example.lebei;

import android.content.Context;
import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;
import androidx.room.migration.Migration;
import androidx.sqlite.db.SupportSQLiteDatabase;

@Database(
        entities = {Word.class, DailyPlan.class, DailyPlanWord.class},
        version = 7,
        exportSchema = false)
public abstract class AppDatabase extends RoomDatabase {

    public abstract WordDao wordDao();

    public abstract DailyPlanDao dailyPlanDao();

    private static final Migration MIGRATION_4_5 =
            new Migration(4, 5) {
                @Override
                public void migrate(SupportSQLiteDatabase database) {
                    database.execSQL(
                            "CREATE TABLE IF NOT EXISTS `daily_plan` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `date_key` TEXT NOT NULL, `book_id` TEXT NOT NULL, `essay_text` TEXT, `target_count` INTEGER NOT NULL)");
                    database.execSQL(
                            "CREATE UNIQUE INDEX IF NOT EXISTS `index_daily_plan_date_key_book_id` ON `daily_plan` (`date_key`, `book_id`)");
                    database.execSQL(
                            "CREATE TABLE IF NOT EXISTS `daily_plan_word` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `daily_plan_id` INTEGER NOT NULL, `word_id` INTEGER NOT NULL, `sort_order` INTEGER NOT NULL, `ai_example_text` TEXT, FOREIGN KEY(`daily_plan_id`) REFERENCES `daily_plan`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE , FOREIGN KEY(`word_id`) REFERENCES `word_table`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE)");
                    database.execSQL(
                            "CREATE INDEX IF NOT EXISTS `index_daily_plan_word_daily_plan_id` ON `daily_plan_word` (`daily_plan_id`)");
                    database.execSQL(
                            "CREATE INDEX IF NOT EXISTS `index_daily_plan_word_word_id` ON `daily_plan_word` (`word_id`)");
                    database.execSQL(
                            "CREATE UNIQUE INDEX IF NOT EXISTS `index_daily_plan_word_daily_plan_id_word_id` ON `daily_plan_word` (`daily_plan_id`, `word_id`)");
                }
            };

    private static final Migration MIGRATION_5_6 =
            new Migration(5, 6) {
                @Override
                public void migrate(SupportSQLiteDatabase database) {
                    database.execSQL(
                            "ALTER TABLE daily_plan_word ADD COLUMN learned INTEGER NOT NULL DEFAULT 0");
                }
            };

    private static final Migration MIGRATION_6_7 =
            new Migration(6, 7) {
                @Override
                public void migrate(SupportSQLiteDatabase database) {
                    database.execSQL(
                            "ALTER TABLE word_table ADD COLUMN difficultyTag INTEGER NOT NULL DEFAULT 0");
                }
            };

    private static AppDatabase INSTANCE;

    public static synchronized AppDatabase getInstance(Context context) {
        if (INSTANCE == null) {
            INSTANCE =
                            Room.databaseBuilder(
                                            context.getApplicationContext(),
                                            AppDatabase.class,
                                            "user_db.db")
                            .addMigrations(MIGRATION_4_5, MIGRATION_5_6, MIGRATION_6_7)
                            .fallbackToDestructiveMigration()
                            .allowMainThreadQueries()
                            .build();
        }
        return INSTANCE;
    }
}
