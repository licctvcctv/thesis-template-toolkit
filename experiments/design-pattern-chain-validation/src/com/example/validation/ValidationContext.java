package com.example.validation;

import java.util.HashMap;
import java.util.Map;

public class ValidationContext {
    private final Map<String, Integer> stockBySku = new HashMap<>();
    private final Map<String, Double> couponThreshold = new HashMap<>();
    private final Map<String, Boolean> frozenUsers = new HashMap<>();

    public ValidationContext() {
        stockBySku.put("BOOK-001", 10);
        stockBySku.put("PHONE-002", 2);
        stockBySku.put("CAMERA-003", 0);
        couponThreshold.put("NEW50", 200.0);
        couponThreshold.put("VIP100", 500.0);
        frozenUsers.put("U009", true);
    }

    public int stockOf(String sku) {
        return stockBySku.getOrDefault(sku, 0);
    }

    public boolean isFrozenUser(String userId) {
        return frozenUsers.getOrDefault(userId, false);
    }

    public boolean couponExists(String couponCode) {
        return couponThreshold.containsKey(couponCode);
    }

    public double couponThreshold(String couponCode) {
        return couponThreshold.getOrDefault(couponCode, Double.MAX_VALUE);
    }
}
