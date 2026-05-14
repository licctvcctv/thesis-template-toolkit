package com.example.validation;

public class HardcodedOrderValidator {
    public ValidationResult validate(OrderForm form, ValidationContext context) {
        ValidationResult result = new ValidationResult();
        result.increaseExecutedRules();
        if (isBlank(form.getOrderId())) {
            result.addError("硬编码必填校验", "orderId", "订单编号不能为空");
            return result;
        }
        if (isBlank(form.getUserId())) {
            result.addError("硬编码必填校验", "userId", "用户编号不能为空");
            return result;
        }
        if (isBlank(form.getPhone())) {
            result.addError("硬编码必填校验", "phone", "手机号不能为空");
            return result;
        }
        if (isBlank(form.getSku())) {
            result.addError("硬编码必填校验", "sku", "商品编号不能为空");
            return result;
        }

        result.increaseExecutedRules();
        if (!form.getPhone().matches("^1[3-9]\\d{9}$")) {
            result.addError("硬编码格式校验", "phone", "手机号格式不符合大陆手机号规则");
            return result;
        }
        if (!form.getOrderId().matches("^OD-\\d{5}$")) {
            result.addError("硬编码格式校验", "orderId", "订单编号必须形如 OD-00001");
            return result;
        }
        if (!form.getSku().matches("^[A-Z]+-\\d{3}$")) {
            result.addError("硬编码格式校验", "sku", "商品编号必须由大写字母和三位数字组成");
            return result;
        }

        result.increaseExecutedRules();
        if (form.getAmount() <= 0) {
            result.addError("硬编码业务校验", "amount", "订单金额必须大于 0");
            return result;
        }
        if (form.getQuantity() <= 0) {
            result.addError("硬编码业务校验", "quantity", "购买数量必须大于 0");
            return result;
        }
        if (form.getAmount() > 3000 && !form.isVip()) {
            result.addError("硬编码业务校验", "amount", "非会员大额订单需要人工审核");
            return result;
        }
        if (context.isFrozenUser(form.getUserId())) {
            result.addError("硬编码业务校验", "userId", "冻结用户不能提交订单");
            return result;
        }

        result.increaseExecutedRules();
        if (form.getRiskScore() >= 80) {
            result.addError("硬编码风险校验", "riskScore", "风险评分过高，需要进入风控复核");
            return result;
        }
        if (form.getAmount() > 1000 && form.getRiskScore() >= 60) {
            result.addError("硬编码风险校验", "riskScore", "高金额订单叠加中高风险评分，需要拦截");
            return result;
        }

        result.increaseExecutedRules();
        int stock = context.stockOf(form.getSku());
        if (stock <= 0) {
            result.addError("硬编码库存校验", "sku", "商品无库存");
            return result;
        }
        if (form.getQuantity() > stock) {
            result.addError("硬编码库存校验", "quantity", "购买数量超过当前库存 " + stock);
        }
        return result;
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
