package com.example.validation;

import java.time.LocalDateTime;

public class OrderForm {
    private final String orderId;
    private final String userId;
    private final String phone;
    private final double amount;
    private final int quantity;
    private final String sku;
    private final String couponCode;
    private final boolean vip;
    private final int riskScore;
    private final LocalDateTime createdAt;

    public OrderForm(String orderId, String userId, String phone, double amount, int quantity,
                     String sku, String couponCode, boolean vip, int riskScore,
                     LocalDateTime createdAt) {
        this.orderId = orderId;
        this.userId = userId;
        this.phone = phone;
        this.amount = amount;
        this.quantity = quantity;
        this.sku = sku;
        this.couponCode = couponCode;
        this.vip = vip;
        this.riskScore = riskScore;
        this.createdAt = createdAt;
    }

    public String getOrderId() {
        return orderId;
    }

    public String getUserId() {
        return userId;
    }

    public String getPhone() {
        return phone;
    }

    public double getAmount() {
        return amount;
    }

    public int getQuantity() {
        return quantity;
    }

    public String getSku() {
        return sku;
    }

    public String getCouponCode() {
        return couponCode;
    }

    public boolean isVip() {
        return vip;
    }

    public int getRiskScore() {
        return riskScore;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public String summary() {
        return orderId + " user=" + userId + " sku=" + sku + " amount=" + amount;
    }
}
