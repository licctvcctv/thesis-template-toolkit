package com.example.validation;

import java.util.ArrayList;
import java.util.List;

public class ChainBuilder {
    private final List<Validator> validators = new ArrayList<>();

    public ChainBuilder add(Validator validator) {
        validators.add(validator);
        return this;
    }

    public ChainBuilder insertAfter(String existingName, Validator validator) {
        for (int i = 0; i < validators.size(); i++) {
            if (validators.get(i).name().equals(existingName)) {
                validators.add(i + 1, validator);
                return this;
            }
        }
        validators.add(validator);
        return this;
    }

    public Validator build() {
        if (validators.isEmpty()) {
            throw new IllegalStateException("职责链至少需要一个校验节点");
        }
        for (int i = 0; i < validators.size() - 1; i++) {
            validators.get(i).linkWith(validators.get(i + 1));
        }
        return validators.get(0);
    }

    public List<String> nodeNames() {
        List<String> names = new ArrayList<>();
        for (Validator validator : validators) {
            names.add(validator.name());
        }
        return names;
    }
}
