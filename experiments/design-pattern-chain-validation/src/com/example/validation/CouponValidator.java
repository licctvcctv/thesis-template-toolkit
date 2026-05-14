package com.example.validation;

public class CouponValidator extends AbstractValidator {
    @Override
    public String name() {
        return "优惠券校验";
    }

    @Override
    protected void validateSelf(OrderForm form, ValidationContext context, ValidationResult result) {
        result.increaseExecutedRules();
        String couponCode = form.getCouponCode();
        if (couponCode == null || couponCode.isBlank()) {
            return;
        }
        if (!context.couponExists(couponCode)) {
            result.addError(name(), "couponCode", "优惠券不存在");
            return;
        }
        double threshold = context.couponThreshold(couponCode);
        if (form.getAmount() < threshold) {
            result.addError(name(), "couponCode", "订单金额未达到优惠券门槛 " + threshold);
        }
        if ("VIP100".equals(couponCode) && !form.isVip()) {
            result.addError(name(), "couponCode", "VIP100 仅会员可使用");
        }
    }
}
