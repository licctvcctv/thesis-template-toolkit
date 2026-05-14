package com.example.validation;

public interface Validator {
    Validator linkWith(Validator next);

    ValidationResult validate(OrderForm form, ValidationContext context);

    String name();
}
