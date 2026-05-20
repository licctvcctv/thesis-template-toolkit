package com.example.lebei;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class MarkdownTextTest {

    @Test
    public void rendersBoldAndBulletLinesAsHtml() {
        assertEquals(
                "<p><strong>Story</strong></p><ul><li>first word</li><li>second word</li></ul>",
                MarkdownText.toHtml("**Story**\n- first word\n- second word"));
    }

    @Test
    public void escapesHtmlBeforeApplyingMarkdown() {
        assertEquals(
                "<p>&lt;word&gt; &amp; <strong>meaning</strong></p>",
                MarkdownText.toHtml("<word> & **meaning**"));
    }
}
