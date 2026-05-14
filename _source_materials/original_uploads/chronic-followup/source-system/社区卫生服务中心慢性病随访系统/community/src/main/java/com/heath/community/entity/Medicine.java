package com.heath.community.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class Medicine {
    private Long id;
    private String medicineCode;
    private String medicineName;
    private String specification;
    private String unit;
    private String manufacturer;
    private BigDecimal price;
    private Integer stock;
    private String description;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
