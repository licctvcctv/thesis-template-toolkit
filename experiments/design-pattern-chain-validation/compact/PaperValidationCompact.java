import java.util.*;
import java.util.regex.Pattern;

public class PaperValidationCompact {
    public static void main(String[] args) {
        Context ctx = Context.demo();
        List<Form> cases = samples();
        Hardcoded hardcoded = new Hardcoded();
        Metrics hardcodedMetrics = run("硬编码校验", cases, hardcoded, ctx);
        ChainBuilder base = new ChainBuilder();
        base.add(new RequiredNode());
        base.add(new FormatNode());
        base.add(new BusinessNode());
        base.add(new RiskNode());
        base.add(new StockNode());
        Metrics chainMetrics = run("基础职责链校验", cases, base.build(), ctx);
        ChainBuilder promotion = new ChainBuilder();
        promotion.add(new RequiredNode());
        promotion.add(new FormatNode());
        promotion.add(new BusinessNode());
        promotion.add(new RiskNode());
        promotion.add(new StockNode());
        promotion.insertAfter("业务规则校验", new CouponNode());
        Metrics promotionMetrics = run("插入优惠券节点后的职责链", cases, promotion.build(), ctx);
        System.out.println("职责链节点: " + base.names());
        System.out.println("动态插入后节点: " + promotion.names());
        System.out.println(hardcodedMetrics.summary());
        System.out.println(chainMetrics.summary());
        System.out.println(promotionMetrics.summary());
    }

    static Metrics run(String name, List<Form> cases, Action action, Context ctx) {
        Metrics metrics = new Metrics(name);
        for (Form form : cases) {
            Result result = action.validate(form, ctx);
            metrics.record(result);
            if (!result.ok()) {
                System.out.println(name + " -> " + form.orderId + " : " + result.first());
            }
        }
        return metrics;
    }

    static List<Form> samples() {
        List<Form> list = new ArrayList<>();
        list.add(new Form("OD-1001", "U-001", "13800000001", "SKU-BOOK", 120.0, 1, "NONE", true, 20));
        list.add(new Form("", "U-002", "13800000002", "SKU-BOOK", 80.0, 1, "NONE", false, 15));
        list.add(new Form("OD-1003", "U-003", "1200", "SKU-BOOK", 88.0, 1, "NONE", false, 10));
        list.add(new Form("OD-1004", "U-004", "13800000004", "SKU-BOOK", 2600.0, 1, "NONE", false, 25));
        list.add(new Form("OD-1005", "U-009", "13800000005", "SKU-BOOK", 90.0, 1, "NONE", true, 12));
        list.add(new Form("OD-1006", "U-006", "13800000006", "SKU-BOOK", 200.0, 1, "NONE", true, 91));
        list.add(new Form("OD-1007", "U-007", "13800000007", "SKU-NONE", 200.0, 1, "NONE", true, 18));
        list.add(new Form("OD-1008", "U-008", "13800000008", "SKU-PHONE", 500.0, 9, "NONE", true, 18));
        list.add(new Form("OD-1009", "U-010", "13800000009", "SKU-BOOK", 180.0, 1, "VIP50", false, 20));
        list.add(new Form("OD-1010", "U-011", "13800000010", "SKU-BOOK", 30.0, 1, "NEW20", true, 20));
        list.add(new Form("OD-1011", "U-012", "13800000011", "SKU-BOOK", 300.0, 2, "NEW20", true, 20));
        return list;
    }

    interface Action {
        Result validate(Form form, Context ctx);
    }

    interface Validator extends Action {
        Validator linkWith(Validator next);
        String name();
    }

    abstract static class Node implements Validator {
        private Validator next;

        public Validator linkWith(Validator next) {
            this.next = next;
            return next;
        }

        public Result validate(Form form, Context ctx) {
            Result result = new Result();
            result.count(name());
            Error error = check(form, ctx);
            if (error != null) {
                result.add(error);
                return result;
            }
            if (next != null) {
                result.merge(next.validate(form, ctx));
            }
            return result;
        }

        abstract Error check(Form form, Context ctx);
    }

    static class RequiredNode extends Node {
        public String name() {
            return "必填字段校验";
        }

        Error check(Form form, Context ctx) {
            if (blank(form.orderId)) {
                return new Error(name(), "orderId", "订单编号不能为空");
            }
            if (blank(form.userId)) {
                return new Error(name(), "userId", "用户编号不能为空");
            }
            if (blank(form.phone)) {
                return new Error(name(), "phone", "手机号不能为空");
            }
            if (blank(form.sku)) {
                return new Error(name(), "sku", "商品编号不能为空");
            }
            return null;
        }
    }

    static class FormatNode extends Node {
        private static final Pattern PHONE = Pattern.compile("^1[3-9]\\d{9}$");

        public String name() {
            return "格式校验";
        }

        Error check(Form form, Context ctx) {
            if (!form.orderId.startsWith("OD-")) {
                return new Error(name(), "orderId", "订单编号必须以 OD- 开头");
            }
            if (!PHONE.matcher(form.phone).matches()) {
                return new Error(name(), "phone", "手机号格式不正确");
            }
            if (!form.sku.startsWith("SKU-")) {
                return new Error(name(), "sku", "商品编号必须以 SKU- 开头");
            }
            return null;
        }
    }

    static class BusinessNode extends Node {
        public String name() {
            return "业务规则校验";
        }

        Error check(Form form, Context ctx) {
            if (ctx.frozen(form.userId)) {
                return new Error(name(), "userId", "冻结用户不能提交订单");
            }
            if (form.amount <= 0) {
                return new Error(name(), "amount", "订单金额必须大于 0");
            }
            if (form.quantity <= 0) {
                return new Error(name(), "quantity", "购买数量必须大于 0");
            }
            if (form.amount > 2000 && !form.vip) {
                return new Error(name(), "amount", "大额订单需要会员身份");
            }
            return null;
        }
    }

    static class CouponNode extends Node {
        public String name() {
            return "优惠券校验";
        }

        Error check(Form form, Context ctx) {
            if (blank(form.coupon) || "NONE".equals(form.coupon)) {
                return null;
            }
            if (!ctx.hasCoupon(form.coupon)) {
                return new Error(name(), "coupon", "优惠券不存在");
            }
            if (form.amount < ctx.min(form.coupon)) {
                return new Error(name(), "amount", "订单金额未达到优惠券门槛");
            }
            if (ctx.memberOnly(form.coupon) && !form.vip) {
                return new Error(name(), "coupon", "会员券只能由会员使用");
            }
            return null;
        }
    }

    static class RiskNode extends Node {
        public String name() {
            return "风险评分校验";
        }

        Error check(Form form, Context ctx) {
            if (form.risk >= ctx.riskLimit) {
                return new Error(name(), "risk", "风险评分超过阈值");
            }
            return null;
        }
    }

    static class StockNode extends Node {
        public String name() {
            return "库存校验";
        }

        Error check(Form form, Context ctx) {
            int stock = ctx.stock(form.sku);
            if (stock <= 0) {
                return new Error(name(), "sku", "商品无库存");
            }
            if (form.quantity > stock) {
                return new Error(name(), "quantity", "购买数量超过库存");
            }
            return null;
        }
    }

    static class ChainBuilder {
        private final List<Validator> nodes = new ArrayList<>();

        ChainBuilder add(Validator node) {
            nodes.add(node);
            return this;
        }

        ChainBuilder insertAfter(String name, Validator node) {
            for (int i = 0; i < nodes.size(); i++) {
                if (nodes.get(i).name().equals(name)) {
                    nodes.add(i + 1, node);
                    return this;
                }
            }
            nodes.add(node);
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

    static class Hardcoded implements Action {
        public Result validate(Form form, Context ctx) {
            Result r = new Result();
            r.count("必填字段校验");
            if (blank(form.orderId)) {
                r.add(new Error("必填字段校验", "orderId", "订单编号不能为空"));
                return r;
            }
            if (blank(form.userId)) {
                r.add(new Error("必填字段校验", "userId", "用户编号不能为空"));
                return r;
            }
            if (blank(form.phone)) {
                r.add(new Error("必填字段校验", "phone", "手机号不能为空"));
                return r;
            }
            if (blank(form.sku)) {
                r.add(new Error("必填字段校验", "sku", "商品编号不能为空"));
                return r;
            }
            r.count("格式校验");
            if (!form.orderId.startsWith("OD-")) {
                r.add(new Error("格式校验", "orderId", "订单编号必须以 OD- 开头"));
                return r;
            }
            if (!Pattern.compile("^1[3-9]\\d{9}$").matcher(form.phone).matches()) {
                r.add(new Error("格式校验", "phone", "手机号格式不正确"));
                return r;
            }
            if (!form.sku.startsWith("SKU-")) {
                r.add(new Error("格式校验", "sku", "商品编号必须以 SKU- 开头"));
                return r;
            }
            r.count("业务规则校验");
            if (ctx.frozen(form.userId)) {
                r.add(new Error("业务规则校验", "userId", "冻结用户不能提交订单"));
                return r;
            }
            if (form.amount <= 0) {
                r.add(new Error("业务规则校验", "amount", "订单金额必须大于 0"));
                return r;
            }
            if (form.quantity <= 0) {
                r.add(new Error("业务规则校验", "quantity", "购买数量必须大于 0"));
                return r;
            }
            if (form.amount > 2000 && !form.vip) {
                r.add(new Error("业务规则校验", "amount", "大额订单需要会员身份"));
                return r;
            }
            r.count("风险评分校验");
            if (form.risk >= ctx.riskLimit) {
                r.add(new Error("风险评分校验", "risk", "风险评分超过阈值"));
                return r;
            }
            r.count("库存校验");
            int stock = ctx.stock(form.sku);
            if (stock <= 0) {
                r.add(new Error("库存校验", "sku", "商品无库存"));
                return r;
            }
            if (form.quantity > stock) {
                r.add(new Error("库存校验", "quantity", "购买数量超过库存"));
                return r;
            }
            return r;
        }
    }

    static class Context {
        final int riskLimit = 90;
        final Map<String, Integer> stock = new HashMap<>();
        final Map<String, Double> couponMin = new HashMap<>();
        final Set<String> memberCoupons = new HashSet<>();
        final Set<String> frozenUsers = new HashSet<>();

        static Context demo() {
            Context c = new Context();
            c.stock.put("SKU-BOOK", 20);
            c.stock.put("SKU-PHONE", 3);
            c.stock.put("SKU-NONE", 0);
            c.couponMin.put("NEW20", 100.0);
            c.couponMin.put("VIP50", 150.0);
            c.memberCoupons.add("VIP50");
            c.frozenUsers.add("U-009");
            return c;
        }

        int stock(String sku) {
            return stock.getOrDefault(sku, 0);
        }

        boolean frozen(String userId) {
            return frozenUsers.contains(userId);
        }

        boolean hasCoupon(String code) {
            return couponMin.containsKey(code);
        }

        double min(String code) {
            return couponMin.getOrDefault(code, 0.0);
        }

        boolean memberOnly(String code) {
            return memberCoupons.contains(code);
        }
    }

    static class Form {
        final String orderId;
        final String userId;
        final String phone;
        final String sku;
        final double amount;
        final int quantity;
        final String coupon;
        final boolean vip;
        final int risk;

        Form(String orderId, String userId, String phone, String sku, double amount, int quantity, String coupon, boolean vip, int risk) {
            this.orderId = orderId;
            this.userId = userId;
            this.phone = phone;
            this.sku = sku;
            this.amount = amount;
            this.quantity = quantity;
            this.coupon = coupon;
            this.vip = vip;
            this.risk = risk;
        }
    }

    static class Result {
        final List<Error> errors = new ArrayList<>();
        final List<String> rules = new ArrayList<>();

        void count(String rule) {
            rules.add(rule);
        }

        void add(Error error) {
            errors.add(error);
        }

        void merge(Result other) {
            rules.addAll(other.rules);
            errors.addAll(other.errors);
        }

        boolean ok() {
            return errors.isEmpty();
        }

        int ruleCount() {
            return rules.size();
        }

        Error first() {
            return errors.isEmpty() ? null : errors.get(0);
        }
    }

    static class Error {
        final String rule;
        final String field;
        final String message;

        Error(String rule, String field, String message) {
            this.rule = rule;
            this.field = field;
            this.message = message;
        }

        public String toString() {
            return rule + "/" + field + "/" + message;
        }
    }

    static class Metrics {
        final String name;
        int total;
        int passed;
        int failed;
        int located;
        int rules;

        Metrics(String name) {
            this.name = name;
        }

        void record(Result result) {
            total++;
            rules += result.ruleCount();
            if (result.ok()) {
                passed++;
            } else {
                failed++;
                if (result.first() != null) {
                    located++;
                }
            }
        }

        String summary() {
            return String.format("%s: total=%d, passed=%d, failed=%d, passRate=%.1f%%, avgRules=%.2f, locationRate=%.1f%%",
                    name, total, passed, failed, rate(passed, total), total == 0 ? 0.0 : rules * 1.0 / total, rate(located, failed));
        }
    }

    static double rate(int value, int base) {
        return base == 0 ? 100.0 : value * 100.0 / base;
    }

    static boolean blank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
