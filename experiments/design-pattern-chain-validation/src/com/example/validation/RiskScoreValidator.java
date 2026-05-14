package com.example.validation;

public class RiskScoreValidator extends AbstractValidator {
    @Override
    public String name() {
        return "风险评分校验";
    }

    @Override
    protected void validateSelf(OrderForm form, ValidationContext context, ValidationResult result) {
        result.increaseExecutedRules();
        if (form.getRiskScore() >= 80) {
            result.addError(name(), "riskScore", "风险评分过高，需要进入风控复核");
        }
        if (form.getAmount() > 1000 && form.getRiskScore() >= 60) {
            result.addError(name(), "riskScore", "高金额订单叠加中高风险评分，需要拦截");
        }
    }
}
