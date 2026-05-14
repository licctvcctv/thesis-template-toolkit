import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

public class PaperValidationDemo {
    public static void main(String[] args) {
        ValidationContext context = ValidationContext.demoContext();
        List<OrderForm> samples = buildSamples();

        HardcodedOrderValidator hardcoded = new HardcodedOrderValidator();
        ExperimentMetrics hardcodedMetrics = runCase(
                "硬编码校验",
                samples,
                (form, ctx) -> hardcoded.validate(form, ctx),
                context
        );

        ChainBuilder baseBuilder = new ChainBuilder()
                .append(new RequiredFieldValidator())
                .append(new FormatValidator())
                .append(new BusinessRuleValidator())
                .append(new RiskScoreValidator())
                .append(new InventoryValidator());

        Validator baseChain = baseBuilder.build();
        ExperimentMetrics chainMetrics = runCase(
                "基础职责链校验",
                samples,
                baseChain,
                context
        );

        ChainBuilder promotionBuilder = new ChainBuilder()
                .append(new RequiredFieldValidator())
                .append(new FormatValidator())
                .append(new BusinessRuleValidator())
                .append(new RiskScoreValidator())
                .append(new InventoryValidator());
        promotionBuilder.insertAfter(
                "业务规则校验",
                new CouponValidator()
        );

        Validator promotionChain = promotionBuilder.build();
        ExperimentMetrics promotionMetrics = runCase(
                "插入优惠券节点后的职责链",
                samples,
                promotionChain,
                context
        );

        System.out.println("职责链节点: " + baseBuilder.names());
        System.out.println("动态插入后节点: " + promotionBuilder.names());
        System.out.println(hardcodedMetrics.summary());
        System.out.println(chainMetrics.summary());
        System.out.println(promotionMetrics.summary());
    }

    private static ExperimentMetrics runCase(
            String name,
            List<OrderForm> samples,
            ValidationAction validator,
            ValidationContext context
    ) {
        ExperimentMetrics metrics = new ExperimentMetrics(name);
        for (OrderForm form : samples) {
            ValidationResult result = validator.validate(form, context);
            metrics.record(result);
            if (!result.passed()) {
                System.out.println(name + " -> " + form.orderId + " : " + result.firstError());
            }
        }
        return metrics;
    }

    private static List<OrderForm> buildSamples() {
        return Arrays.asList(
                new OrderForm("OD-1001", "U-001", "13800000001", "SKU-BOOK", 120.0, 1, "NONE", true, 20),
                new OrderForm("", "U-002", "13800000002", "SKU-BOOK", 80.0, 1, "NONE", false, 15),
                new OrderForm("OD-1003", "U-003", "1200", "SKU-BOOK", 88.0, 1, "NONE", false, 10),
                new OrderForm("OD-1004", "U-004", "13800000004", "SKU-BOOK", 2600.0, 1, "NONE", false, 25),
                new OrderForm("OD-1005", "U-009", "13800000005", "SKU-BOOK", 90.0, 1, "NONE", true, 12),
                new OrderForm("OD-1006", "U-006", "13800000006", "SKU-BOOK", 200.0, 1, "NONE", true, 91),
                new OrderForm("OD-1007", "U-007", "13800000007", "SKU-NONE", 200.0, 1, "NONE", true, 18),
                new OrderForm("OD-1008", "U-008", "13800000008", "SKU-PHONE", 500.0, 9, "NONE", true, 18),
                new OrderForm("OD-1009", "U-010", "13800000009", "SKU-BOOK", 180.0, 1, "VIP50", false, 20),
                new OrderForm("OD-1010", "U-011", "13800000010", "SKU-BOOK", 30.0, 1, "NEW20", true, 20),
                new OrderForm("OD-1011", "U-012", "13800000011", "SKU-BOOK", 300.0, 2, "NEW20", true, 20)
        );
    }

    interface Validator extends ValidationAction {
        Validator linkWith(
                Validator next
        );

        String name();
    }

    interface ValidationAction {
        ValidationResult validate(
                OrderForm form,
                ValidationContext context
        );
    }

    abstract static class AbstractValidator implements Validator {
        private Validator next;

        public Validator linkWith(
                Validator next
        ) {
            this.next = next;
            return next;
        }

        public ValidationResult validate(
                OrderForm form,
                ValidationContext context
        ) {
            ValidationResult current = new ValidationResult();
            current.countRule(name());
            ValidationError error = check(form, context);
            if (error != null) {
                current.addError(error);
                return current;
            }
            if (next == null) {
                return current;
            }
            current.merge(next.validate(form, context));
            return current;
        }

        protected abstract ValidationError check(
                OrderForm form,
                ValidationContext context
        );
    }

    static class RequiredFieldValidator extends AbstractValidator {
        public String name() {
            return "必填字段校验";
        }

        protected ValidationError check(
                OrderForm form,
                ValidationContext context
        ) {
            if (blank(form.orderId)) {
                return new ValidationError(name(), "orderId", "订单编号不能为空");
            }
            if (blank(form.userId)) {
                return new ValidationError(name(), "userId", "用户编号不能为空");
            }
            if (blank(form.phone)) {
                return new ValidationError(name(), "phone", "手机号不能为空");
            }
            if (blank(form.sku)) {
                return new ValidationError(name(), "sku", "商品编号不能为空");
            }
            return null;
        }
    }

    static class FormatValidator extends AbstractValidator {
        private static final Pattern PHONE = Pattern.compile("^1[3-9]\\d{9}$");

        public String name() {
            return "格式校验";
        }

        protected ValidationError check(
                OrderForm form,
                ValidationContext context
        ) {
            if (!form.orderId.startsWith("OD-")) {
                return new ValidationError(name(), "orderId", "订单编号必须以 OD- 开头");
            }
            if (!PHONE.matcher(form.phone).matches()) {
                return new ValidationError(name(), "phone", "手机号格式不正确");
            }
            if (!form.sku.startsWith("SKU-")) {
                return new ValidationError(name(), "sku", "商品编号必须以 SKU- 开头");
            }
            return null;
        }
    }

    static class BusinessRuleValidator extends AbstractValidator {
        public String name() {
            return "业务规则校验";
        }

        protected ValidationError check(
                OrderForm form,
                ValidationContext context
        ) {
            if (context.isFrozen(form.userId)) {
                return new ValidationError(name(), "userId", "冻结用户不能提交订单");
            }
            if (form.amount <= 0) {
                return new ValidationError(name(), "amount", "订单金额必须大于 0");
            }
            if (form.quantity <= 0) {
                return new ValidationError(name(), "quantity", "购买数量必须大于 0");
            }
            if (form.amount > 2000 && !form.vip) {
                return new ValidationError(name(), "amount", "大额订单需要会员身份");
            }
            return null;
        }
    }

    static class CouponValidator extends AbstractValidator {
        public String name() {
            return "优惠券校验";
        }

        protected ValidationError check(
                OrderForm form,
                ValidationContext context
        ) {
            if (blank(form.couponCode) || "NONE".equals(form.couponCode)) {
                return null;
            }
            if (!context.hasCoupon(form.couponCode)) {
                return new ValidationError(name(), "couponCode", "优惠券不存在");
            }
            if (form.amount < context.minAmount(form.couponCode)) {
                return new ValidationError(name(), "amount", "订单金额未达到优惠券门槛");
            }
            if (context.memberOnly(form.couponCode) && !form.vip) {
                return new ValidationError(name(), "couponCode", "会员券只能由会员使用");
            }
            return null;
        }
    }

    static class RiskScoreValidator extends AbstractValidator {
        public String name() {
            return "风险评分校验";
        }

        protected ValidationError check(
                OrderForm form,
                ValidationContext context
        ) {
            if (form.riskScore >= context.riskLimit) {
                return new ValidationError(name(), "riskScore", "风险评分超过阈值");
            }
            return null;
        }
    }

    static class InventoryValidator extends AbstractValidator {
        public String name() {
            return "库存校验";
        }

        protected ValidationError check(
                OrderForm form,
                ValidationContext context
        ) {
            int stock = context.stockOf(form.sku);
            if (stock <= 0) {
                return new ValidationError(name(), "sku", "商品无库存");
            }
            if (form.quantity > stock) {
                return new ValidationError(name(), "quantity", "购买数量超过库存");
            }
            return null;
        }
    }

    static class ChainBuilder {
        private final List<Validator> nodes = new ArrayList<>();

        ChainBuilder append(
                Validator validator
        ) {
            nodes.add(validator);
            return this;
        }

        ChainBuilder insertAfter(
                String nodeName,
                Validator validator
        ) {
            for (int i = 0; i < nodes.size(); i++) {
                if (nodes.get(i).name().equals(nodeName)) {
                    nodes.add(i + 1, validator);
                    return this;
                }
            }
            nodes.add(validator);
            return this;
        }

        Validator build() {
            for (int i = 0; i < nodes.size(); i++) {
                Validator next = i + 1 < nodes.size() ? nodes.get(i + 1) : null;
                nodes.get(i).linkWith(next);
            }
            return nodes.get(0);
        }

        List<String> names() {
            List<String> names = new ArrayList<>();
            for (Validator node : nodes) {
                names.add(node.name());
            }
            return names;
        }
    }

    static class HardcodedOrderValidator {
        ValidationResult validate(
                OrderForm form,
                ValidationContext context
        ) {
            ValidationResult result = new ValidationResult();
            result.countRule("必填字段校验");
            if (blank(form.orderId)) {
                result.addError(new ValidationError("必填字段校验", "orderId", "订单编号不能为空"));
                return result;
            }
            if (blank(form.userId)) {
                result.addError(new ValidationError("必填字段校验", "userId", "用户编号不能为空"));
                return result;
            }
            if (blank(form.phone)) {
                result.addError(new ValidationError("必填字段校验", "phone", "手机号不能为空"));
                return result;
            }
            if (blank(form.sku)) {
                result.addError(new ValidationError("必填字段校验", "sku", "商品编号不能为空"));
                return result;
            }

            result.countRule("格式校验");
            if (!form.orderId.startsWith("OD-")) {
                result.addError(new ValidationError("格式校验", "orderId", "订单编号必须以 OD- 开头"));
                return result;
            }
            if (!Pattern.compile("^1[3-9]\\d{9}$").matcher(form.phone).matches()) {
                result.addError(new ValidationError("格式校验", "phone", "手机号格式不正确"));
                return result;
            }
            if (!form.sku.startsWith("SKU-")) {
                result.addError(new ValidationError("格式校验", "sku", "商品编号必须以 SKU- 开头"));
                return result;
            }

            result.countRule("业务规则校验");
            if (context.isFrozen(form.userId)) {
                result.addError(new ValidationError("业务规则校验", "userId", "冻结用户不能提交订单"));
                return result;
            }
            if (form.amount <= 0) {
                result.addError(new ValidationError("业务规则校验", "amount", "订单金额必须大于 0"));
                return result;
            }
            if (form.quantity <= 0) {
                result.addError(new ValidationError("业务规则校验", "quantity", "购买数量必须大于 0"));
                return result;
            }
            if (form.amount > 2000 && !form.vip) {
                result.addError(new ValidationError("业务规则校验", "amount", "大额订单需要会员身份"));
                return result;
            }

            result.countRule("风险评分校验");
            if (form.riskScore >= context.riskLimit) {
                result.addError(new ValidationError("风险评分校验", "riskScore", "风险评分超过阈值"));
                return result;
            }

            result.countRule("库存校验");
            int stock = context.stockOf(form.sku);
            if (stock <= 0) {
                result.addError(new ValidationError("库存校验", "sku", "商品无库存"));
                return result;
            }
            if (form.quantity > stock) {
                result.addError(new ValidationError("库存校验", "quantity", "购买数量超过库存"));
                return result;
            }
            return result;
        }
    }

    static class ValidationContext {
        private final Map<String, Integer> stock = new HashMap<>();
        private final Map<String, Double> couponMin = new HashMap<>();
        private final Set<String> memberCoupons = new HashSet<>();
        private final Set<String> frozenUsers = new HashSet<>();
        private final int riskLimit = 90;

        static ValidationContext demoContext() {
            ValidationContext context = new ValidationContext();
            context.stock.put("SKU-BOOK", 20);
            context.stock.put("SKU-PHONE", 3);
            context.stock.put("SKU-NONE", 0);
            context.couponMin.put("NEW20", 100.0);
            context.couponMin.put("VIP50", 150.0);
            context.memberCoupons.add("VIP50");
            context.frozenUsers.add("U-009");
            return context;
        }

        int stockOf(
                String sku
        ) {
            return stock.getOrDefault(sku, 0);
        }

        boolean isFrozen(
                String userId
        ) {
            return frozenUsers.contains(userId);
        }

        boolean hasCoupon(
                String code
        ) {
            return couponMin.containsKey(code);
        }

        double minAmount(
                String code
        ) {
            return couponMin.getOrDefault(code, 0.0);
        }

        boolean memberOnly(
                String code
        ) {
            return memberCoupons.contains(code);
        }
    }

    static class OrderForm {
        final String orderId;
        final String userId;
        final String phone;
        final String sku;
        final double amount;
        final int quantity;
        final String couponCode;
        final boolean vip;
        final int riskScore;

        OrderForm(
                String orderId,
                String userId,
                String phone,
                String sku,
                double amount,
                int quantity,
                String couponCode,
                boolean vip,
                int riskScore
        ) {
            this.orderId = orderId;
            this.userId = userId;
            this.phone = phone;
            this.sku = sku;
            this.amount = amount;
            this.quantity = quantity;
            this.couponCode = couponCode;
            this.vip = vip;
            this.riskScore = riskScore;
        }
    }

    static class ValidationResult {
        private final List<ValidationError> errors = new ArrayList<>();
        private final List<String> executedRules = new ArrayList<>();

        void countRule(
                String rule
        ) {
            executedRules.add(rule);
        }

        void addError(
                ValidationError error
        ) {
            errors.add(error);
        }

        void merge(
                ValidationResult other
        ) {
            executedRules.addAll(other.executedRules);
            errors.addAll(other.errors);
        }

        boolean passed() {
            return errors.isEmpty();
        }

        int executedRuleCount() {
            return executedRules.size();
        }

        ValidationError firstError() {
            return errors.isEmpty() ? null : errors.get(0);
        }
    }

    static class ValidationError {
        final String ruleName;
        final String fieldName;
        final String message;

        ValidationError(
                String ruleName,
                String fieldName,
                String message
        ) {
            this.ruleName = ruleName;
            this.fieldName = fieldName;
            this.message = message;
        }

        public String toString() {
            return ruleName + "/" + fieldName + "/" + message;
        }
    }

    static class ExperimentMetrics {
        private final String name;
        private int total;
        private int passed;
        private int failed;
        private int located;
        private int executedRules;

        ExperimentMetrics(
                String name
        ) {
            this.name = name;
        }

        void record(
                ValidationResult result
        ) {
            total++;
            executedRules += result.executedRuleCount();
            if (result.passed()) {
                passed++;
            } else {
                failed++;
                if (result.firstError() != null) {
                    located++;
                }
            }
        }

        String summary() {
            return String.format(
                    "%s: total=%d, passed=%d, failed=%d, passRate=%.1f%%, avgRules=%.2f, locationRate=%.1f%%",
                    name,
                    total,
                    passed,
                    failed,
                    total == 0 ? 0.0 : passed * 100.0 / total,
                    total == 0 ? 0.0 : executedRules * 1.0 / total,
                    failed == 0 ? 100.0 : located * 100.0 / failed
            );
        }
    }

    private static boolean blank(
            String value
    ) {
        return value == null || value.trim().isEmpty();
    }
}
