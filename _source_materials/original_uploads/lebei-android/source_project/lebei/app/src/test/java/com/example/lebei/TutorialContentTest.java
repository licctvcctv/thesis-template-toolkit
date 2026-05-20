package com.example.lebei;

import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class TutorialContentTest {

    @Test
    public void learnGuideMentionsAiExampleAndEasyHardChoice() {
        String guide = TutorialContent.learnGuide();

        assertTrue(guide.contains("AI例句"));
        assertTrue(guide.contains("简单"));
        assertTrue(guide.contains("困难"));
    }
}
