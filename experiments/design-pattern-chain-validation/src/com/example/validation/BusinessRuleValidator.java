package com.example.validation;

public class BusinessRuleValidator extends AbstractValidator {
    @Override
    public String name() {
        return "业务规则校验";
    }

    @Override
    protected void validateSelf(OrderForm form, ValidationContext context, ValidationResult result) {
        result.increaseExecutedRules();
        if (form.getAmount() <= 0) {
            result.addError(name(), "amount", "订单金额必须大于 0");
        }
        if (form.getQuantity() <= 0) {
            result.addError(name(), "quantity", "购买数量必须大于 0");
        }
        if (form.getAmount() > 3000 && !form.isVip()) {
            result.addError(name(), "amount", "非会员订单金额超过 3000 元需要人工审核");
        }
        if (context.isFrozenUser(form.getUserId())) {
            result.addError(name(), "userId", "冻结用户不能提交订单");
        }
    }
}
