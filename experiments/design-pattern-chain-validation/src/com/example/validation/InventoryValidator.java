package com.example.validation;

public class InventoryValidator extends AbstractValidator {
    @Override
    public String name() {
        return "库存校验";
    }

    @Override
    protected void validateSelf(OrderForm form, ValidationContext context, ValidationResult result) {
        result.increaseExecutedRules();
        int stock = context.stockOf(form.getSku());
        if (stock <= 0) {
            result.addError(name(), "sku", "商品无库存");
        } else if (form.getQuantity() > stock) {
            result.addError(name(), "quantity", "购买数量超过当前库存 " + stock);
        }
    }
}
