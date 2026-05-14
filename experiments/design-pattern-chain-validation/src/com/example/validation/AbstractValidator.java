package com.example.validation;

public abstract class AbstractValidator implements Validator {
    private Validator next;

    @Override
    public Validator linkWith(Validator next) {
        this.next = next;
        return next;
    }

    @Override
    public ValidationResult validate(OrderForm form, ValidationContext context) {
        ValidationResult result = new ValidationResult();
        validateSelf(form, context, result);
        if (result.passed() && next != null) {
            ValidationResult nextResult = next.validate(form, context);
            merge(result, nextResult);
        }
        return result;
    }

    protected abstract void validateSelf(OrderForm form, ValidationContext context,
                                         ValidationResult result);

    protected boolean blank(String value) {
        return value == null || value.trim().isEmpty();
    }

    private void merge(ValidationResult target, ValidationResult source) {
        for (ValidationError error : source.getErrors()) {
            target.addError(error.getRuleName(), error.getFieldName(), error.getMessage());
        }
        for (int i = 0; i < source.getExecutedRules(); i++) {
            target.increaseExecutedRules();
        }
    }
}
