package com.example.validation;

public class FormatValidator extends AbstractValidator {
    @Override
    public String name() {
        return "格式校验";
    }

    @Override
    protected void validateSelf(OrderForm form, ValidationContext context, ValidationResult result) {
        result.increaseExecutedRules();
        if (!form.getPhone().matches("^1[3-9]\\d{9}$")) {
            result.addError(name(), "phone", "手机号格式不符合大陆手机号规则");
        }
        if (!form.getOrderId().matches("^OD-\\d{5}$")) {
            result.addError(name(), "orderId", "订单编号必须形如 OD-00001");
        }
        if (!form.getSku().matches("^[A-Z]+-\\d{3}$")) {
            result.addError(name(), "sku", "商品编号必须由大写字母和三位数字组成");
        }
    }
}
