package com.example.lebei;

import android.content.Context;
import android.content.res.AssetManager;
import android.util.Log;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class DataProvider {

    private static final String TAG = "DataProvider";

    /** 与 assets 中文件名一致（不含 .csv 即为 bookId） */
    private static final String[] BOOK_CSV_FILES = {
        "JUNIOR_HIGH.csv",
        "SENIOR_HIGH.csv",
        "CET4.csv",
        "CET6.csv",
        "IELTS.csv",
        "TOEFL.csv"
    };

    /**
     * 保证各词库在本地都有词条：首次全量导入；升级后若某 bookId 仍为空则只补该词库。
     * 避免历史上只打过 CET4 包时，用户选雅思等计划却抽不到词。
     */
    public static void ensureVocabularyFromAssets(Context context, AppDatabase db) {
        WordDao dao = db.wordDao();
        AssetManager assetManager = context.getAssets();
        int totalInserted = 0;
        for (String fileName : BOOK_CSV_FILES) {
            if (fileName.length() < 5 || !fileName.endsWith(".csv")) {
                continue;
            }
            String bookId = fileName.substring(0, fileName.length() - 4);
            try {
                if (dao.countWordsInBook(bookId) > 0) {
                    repairDifficultyTagsIfNeeded(dao, assetManager, fileName, bookId);
                    continue;
                }
            } catch (Exception e) {
                Log.w(TAG, "countWordsInBook " + bookId, e);
            }
            List<Word> batch = readWordsFromAsset(assetManager, fileName);
            if (!batch.isEmpty()) {
                try {
                    dao.insertAll(batch);
                    totalInserted += batch.size();
                    Log.d(TAG, "补全词库 " + bookId + "，写入 " + batch.size() + " 词");
                } catch (Exception e) {
                    Log.e(TAG, "insertAll " + bookId, e);
                }
            }
        }
        if (totalInserted > 0) {
            Log.d(TAG, "ensureVocabularyFromAssets 本轮共写入 " + totalInserted + " 词");
        }
    }

    private static void repairDifficultyTagsIfNeeded(
            WordDao dao, AssetManager assetManager, String fileName, String bookId) {
        try {
            if (dao.countDifficultyTaggedWordsInBook(bookId) > 0) {
                return;
            }
            List<Word> words = readWordsFromAsset(assetManager, fileName);
            for (Word w : words) {
                if (w.difficultyTag != 0) {
                    dao.updateDifficultyTag(bookId, w.word, w.difficultyTag);
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "repairDifficultyTags " + bookId, e);
        }
    }

    /**
     * @deprecated 请使用 {@link #ensureVocabularyFromAssets}，以支持增量补全各 bookId。
     */
    @Deprecated
    public static void importWordsFromAssets(Context context, AppDatabase db) {
        ensureVocabularyFromAssets(context, db);
    }

    private static List<Word> readWordsFromAsset(AssetManager assetManager, String fileName) {
        List<Word> words = new ArrayList<>();
        try (InputStream is = assetManager.open(fileName);
                BufferedReader reader =
                        new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {
            String line;
            boolean isFirstLine = true;
            while ((line = reader.readLine()) != null) {
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }
                String[] parts = line.split(",");
                if (parts.length >= 4) {
                    String word = parts[0].trim();
                    String phonetic = parts[1].trim();
                    String translation = parts[2].trim();
                    String bookId = parts[3].trim();
                    int difficultyTag = parts.length >= 5 ? parseDifficultyTag(parts[4]) : 0;
                    words.add(new Word(word, phonetic, translation, bookId, difficultyTag));
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "读取 " + fileName + " 失败: " + e.getMessage());
        }
        return words;
    }

    private static int parseDifficultyTag(String raw) {
        try {
            return Integer.parseInt(raw.trim()) == 1 ? 1 : 0;
        } catch (Exception ignored) {
            return 0;
        }
    }
}
