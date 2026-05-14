package com.example.validation;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class ExperimentRunner {
    public static void main(String[] args) {
        ValidationContext context = new ValidationContext();
        List<OrderForm> samples = sampleOrders();
        HardcodedOrderValidator hardcodedValidator = new HardcodedOrderValidator();

        ChainBuilder builder = new ChainBuilder()
                .add(new RequiredFieldValidator())
                .add(new FormatValidator())
                .add(new BusinessRuleValidator())
                .add(new RiskScoreValidator())
                .add(new InventoryValidator());
        Validator chain = builder.build();

        ChainBuilder extendedBuilder = new ChainBuilder()
                .add(new RequiredFieldValidator())
                .add(new FormatValidator())
                .add(new BusinessRuleValidator())
                .insertAfter("业务规则校验", new CouponValidator())
                .add(new RiskScoreValidator())
                .add(new InventoryValidator());
        Validator extendedChain = extendedBuilder.build();

        ExperimentMetrics hardcodedMetrics = runHardcoded(samples, context, hardcodedValidator);
        ExperimentMetrics chainMetrics = runChain(samples, context, chain);
        ExperimentMetrics extendedMetrics = runChain(samples, context, extendedChain);

        System.out.println("=== 表单校验职责链实验 ===");
        System.out.println("职责链节点: " + builder.nodeNames());
        System.out.println("动态插入后节点: " + extendedBuilder.nodeNames());
        System.out.println(hardcodedMetrics.summary("硬编码校验"));
        System.out.println(chainMetrics.summary("职责链校验"));
        System.out.println(extendedMetrics.summary("插入优惠券节点后的职责链"));
        printDetailedFailures(samples, context, extendedChain);
    }

    private static ExperimentMetrics runHardcoded(List<OrderForm> samples, ValidationContext context,
                                                  HardcodedOrderValidator validator) {
        ExperimentMetrics metrics = new ExperimentMetrics();
        for (OrderForm sample : samples) {
            metrics.record(validator.validate(sample, context));
        }
        return metrics;
    }

    private static ExperimentMetrics runChain(List<OrderForm> samples, ValidationContext context,
                                              Validator validator) {
        ExperimentMetrics metrics = new ExperimentMetrics();
        for (OrderForm sample : samples) {
            metrics.record(validator.validate(sample, context));
        }
        return metrics;
    }

    private static void printDetailedFailures(List<OrderForm> samples, ValidationContext context,
                                              Validator validator) {
        System.out.println("--- 失败样本定位 ---");
        for (OrderForm sample : samples) {
            ValidationResult result = validator.validate(sample, context);
            if (!result.passed()) {
                System.out.println(sample.summary());
                for (ValidationError error : result.getErrors()) {
                    System.out.println("  " + error);
                }
            }
        }
    }

    private static List<OrderForm> sampleOrders() {
        List<OrderForm> samples = new ArrayList<>();
        samples.add(new OrderForm("OD-00001", "U001", "13800138000", 299.0, 1,
                "BOOK-001", "NEW50", false, 20, LocalDateTime.now()));
        samples.add(new OrderForm("", "U002", "13800138001", 199.0, 1,
                "BOOK-001", null, false, 10, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00002", "U003", "12800138000", 199.0, 1,
                "BOOK-001", null, false, 10, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00003", "U004", "13900139000", 4200.0, 1,
                "PHONE-002", null, false, 30, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00004", "U009", "13700137000", 120.0, 1,
                "BOOK-001", null, false, 20, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00005", "U005", "13600136000", 1200.0, 1,
                "PHONE-002", null, true, 70, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00006", "U006", "13500135000", 88.0, 1,
                "CAMERA-003", null, false, 5, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00007", "U007", "13400134000", 99.0, 20,
                "BOOK-001", null, false, 5, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00008", "U008", "13300133000", 650.0, 1,
                "BOOK-001", "VIP100", false, 10, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00009", "U010", "13200132000", 180.0, 1,
                "BOOK-001", "NEW50", false, 10, LocalDateTime.now()));
        samples.add(new OrderForm("OD-00010", "U011", "13100131000", 900.0, 1,
                "PHONE-002", "VIP100", true, 20, LocalDateTime.now()));
        return samples;
    }
}
