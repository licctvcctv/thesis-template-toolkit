package com.example.lebei;

public final class TutorialContent {

    private TutorialContent() {}

    public static String learnGuide() {
        return "1. 点击「查看 AI例句」可以为当前单词生成例句。\n"
                + "2. 若觉得当前词汇简单，选择「简单」；反之选择「困难」。\n"
                + "3. 当天新词学完后会进入复习环节，复习时根据中文释义拼写英文。\n"
                + "4. 可以生成今日复习短文，短文会保存在回顾页。";
    }

    public static String planGuide() {
        return "1. 选择词库后，设置每日新词数和每日复习数。\n"
                + "2. 修改词书和计划后通常次日生效，今天已生成的计划不会被打乱。\n"
                + "3. 复习数越高，到期旧词出现越充分。";
    }

    public static String statisticsGuide() {
        return "1. 这里统计累计学习、已掌握、总复习次数和学习天数。\n"
                + "2. 「限时拼写挑战」是游戏入口，限定时间内拼对即可加分。\n"
                + "3. 「查看排行榜」可查看学习积分和掌握词汇排名。";
    }

    public static String historyGuide() {
        return "1. 回顾页按日期展示每日学习计划。\n"
                + "2. 点进某一天可以查看当日单词、AI 例句和已生成的短文。\n"
                + "3. 如果还没有记录，先在学习页完成单词或生成短文。";
    }
}
