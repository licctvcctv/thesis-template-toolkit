package com.example.validation;

public class ValidationError {
    private final String ruleName;
    private final String fieldName;
    private final String message;

    public ValidationError(String ruleName, String fieldName, String message) {
        this.ruleName = ruleName;
        this.fieldName = fieldName;
        this.message = message;
    }

    public String getRuleName() {
        return ruleName;
    }

    public String getFieldName() {
        return fieldName;
    }

    public String getMessage() {
        return message;
    }

    @Override
    public String toString() {
        return "[" + ruleName + "] " + fieldName + ": " + message;
    }
}
