package com.example.lebei;

public final class MarkdownText {

    private MarkdownText() {}

    public static String toHtml(String markdown) {
        if (markdown == null || markdown.trim().isEmpty()) {
            return "";
        }
        String[] lines = markdown.replace("\r\n", "\n").replace('\r', '\n').split("\n");
        StringBuilder html = new StringBuilder();
        boolean inList = false;
        StringBuilder paragraph = new StringBuilder();

        for (String rawLine : lines) {
            String line = rawLine.trim();
            if (line.isEmpty()) {
                if (paragraph.length() > 0) {
                    appendParagraph(html, paragraph.toString());
                    paragraph.setLength(0);
                }
                if (inList) {
                    html.append("</ul>");
                    inList = false;
                }
                continue;
            }
            if (line.startsWith("- ") || line.startsWith("* ")) {
                if (paragraph.length() > 0) {
                    appendParagraph(html, paragraph.toString());
                    paragraph.setLength(0);
                }
                if (!inList) {
                    html.append("<ul>");
                    inList = true;
                }
                html.append("<li>").append(formatInline(line.substring(2).trim())).append("</li>");
                continue;
            }
            if (inList) {
                html.append("</ul>");
                inList = false;
            }
            if (paragraph.length() > 0) {
                paragraph.append("<br>");
            }
            paragraph.append(formatInline(line));
        }
        if (paragraph.length() > 0) {
            appendParagraph(html, paragraph.toString());
        }
        if (inList) {
            html.append("</ul>");
        }
        return html.toString();
    }

    private static void appendParagraph(StringBuilder html, String content) {
        html.append("<p>").append(content).append("</p>");
    }

    private static String formatInline(String text) {
        String escaped = escapeHtml(text);
        return escaped
                .replaceAll("\\*\\*(.+?)\\*\\*", "<strong>$1</strong>")
                .replaceAll("__(.+?)__", "<strong>$1</strong>")
                .replaceAll("\\*(.+?)\\*", "<em>$1</em>")
                .replaceAll("_(.+?)_", "<em>$1</em>");
    }

    private static String escapeHtml(String text) {
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }
}
