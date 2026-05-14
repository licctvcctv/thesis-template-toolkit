package com.example.validation;

public class RequiredFieldValidator extends AbstractValidator {
    @Override
    public String name() {
        return "必填字段校验";
    }

    @Override
    protected void validateSelf(OrderForm form, ValidationContext context, ValidationResult result) {
        result.increaseExecutedRules();
        if (blank(form.getOrderId())) {
            result.addError(name(), "orderId", "订单编号不能为空");
        }
        if (blank(form.getUserId())) {
            result.addError(name(), "userId", "用户编号不能为空");
        }
        if (blank(form.getPhone())) {
            result.addError(name(), "phone", "手机号不能为空");
        }
        if (blank(form.getSku())) {
            result.addError(name(), "sku", "商品编号不能为空");
        }
    }
}
