package com.example.validation;

public class ExperimentMetrics {
    private int total;
    private int passed;
    private int failed;
    private int executedRules;
    private int locatedByFirstRule;

    public void record(ValidationResult result) {
        total++;
        executedRules += result.getExecutedRules();
        if (result.passed()) {
            passed++;
        } else {
            failed++;
            if (!"NONE".equals(result.firstErrorRule())) {
                locatedByFirstRule++;
            }
        }
    }

    public double passRate() {
        return total == 0 ? 0.0 : passed * 100.0 / total;
    }

    public double averageRules() {
        return total == 0 ? 0.0 : executedRules * 1.0 / total;
    }

    public double locationRate() {
        return failed == 0 ? 100.0 : locatedByFirstRule * 100.0 / failed;
    }

    public String summary(String name) {
        return String.format(
                "%s: total=%d, passed=%d, failed=%d, passRate=%.1f%%, avgRules=%.2f, locationRate=%.1f%%",
                name, total, passed, failed, passRate(), averageRules(), locationRate());
    }
}
