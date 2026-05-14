package com.example.validation;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ValidationResult {
    private final List<ValidationError> errors = new ArrayList<>();
    private int executedRules;

    public void addError(String ruleName, String fieldName, String message) {
        errors.add(new ValidationError(ruleName, fieldName, message));
    }

    public void increaseExecutedRules() {
        executedRules++;
    }

    public boolean passed() {
        return errors.isEmpty();
    }

    public int getExecutedRules() {
        return executedRules;
    }

    public List<ValidationError> getErrors() {
        return Collections.unmodifiableList(errors);
    }

    public String firstErrorRule() {
        if (errors.isEmpty()) {
            return "NONE";
        }
        return errors.get(0).getRuleName();
    }
}
